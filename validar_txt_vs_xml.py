#!/usr/bin/env python3
"""
Script para validar TXTs gerados vs XMLs originais
Cruza produtos e quantidades para verificar se batem
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict


def extract_mapa_number(filename):
    """Extrai número do mapa do nome do arquivo"""
    for pattern in [r'mapa[_-](\d+)', r'ocp[_-](\d+)', r'map_(\d+)']:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def parse_xml_quantities(xml_path):
    """Extrai produtos e quantidades do XML"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        products = defaultdict(int)

        # Estrutura 1: XML de entrada (meus_xmls) - formato OCP
        for item in root.findall(".//item"):
            code_elem = item.find("cdItem")
            qty_venda_elem = item.find("qtUnVenda")
            qty_avulsa_elem = item.find("qtUnAvulsa")

            if code_elem is not None and qty_venda_elem is not None:
                code = code_elem.text.strip()
                qty_venda = int(qty_venda_elem.text) if qty_venda_elem.text else 0
                qty_avulsa = int(qty_avulsa_elem.text) if qty_avulsa_elem is not None and qty_avulsa_elem.text else 0
                products[code] += qty_venda + qty_avulsa

        # Estrutura 2: XML convertido (se existir)
        for item in root.findall(".//Item"):
            code_elem = item.find(".//Code")
            qty_elem = item.find(".//Quantity")

            if code_elem is not None and qty_elem is not None:
                code = code_elem.text.strip()
                qty = int(qty_elem.text)
                products[code] += qty

        return products
    except Exception as e:
        print(f"Erro ao ler XML {xml_path}: {e}")
        return {}


def parse_txt_quantities(txt_path):
    """Extrai produtos e quantidades do TXT"""
    products = defaultdict(int)

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(r"\s*\|\s*\d+\s+(\d+)\s+.*?\s+(\d+)\s+\d+\s+\d+/\d+", line)
                if match:
                    code = match.group(1)
                    qty = int(match.group(2))
                    products[code] += qty

        return products
    except Exception as e:
        print(f"Erro ao ler TXT {txt_path}: {e}")
        return {}


def compare_products(xml_products, txt_products):
    """Compara produtos entre XML e TXT"""
    issues = []

    missing_in_txt = set(xml_products.keys()) - set(txt_products.keys())
    if missing_in_txt:
        issues.append(f"  ⚠️  Produtos no XML mas NÃO no TXT: {missing_in_txt}")

    extra_in_txt = set(txt_products.keys()) - set(xml_products.keys())
    if extra_in_txt:
        issues.append(f"  ⚠️  Produtos no TXT mas NÃO no XML: {extra_in_txt}")

    qty_diff = []
    for code in xml_products.keys() & txt_products.keys():
        if xml_products[code] != txt_products[code]:
            qty_diff.append(f"    Produto {code}: XML={xml_products[code]} vs TXT={txt_products[code]}")

    if qty_diff:
        issues.append("  ⚠️  Quantidades diferentes:")
        issues.extend(qty_diff)

    return issues


def generate_markdown_report(mapas_ok, mapas_com_divergencias, total_ok, total_issues, total_not_found, total_files):
    """Gera relatório detalhado em markdown com foco nos mapas validados com sucesso"""

    report_path = Path("/mnt/c/prd_debian/VALIDACAO_TXT_vs_XML.md")

    if total_files == 0:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# ✅ Relatório de Validação: XMLs vs TXTs\n\n")
            f.write("Nenhum TXT encontrado para validar.\n")
        print(f"Relatório salvo: {report_path}")
        return

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# ✅ Relatório de Validação: XMLs vs TXTs - Mapas com Sucesso\n\n")
        f.write(f"- **Total de mapas processados:** {total_files}\n")
        f.write(f"- **✅ Mapas validados com sucesso:** {total_ok} ({total_ok/total_files*100:.1f}%)\n")
        f.write(f"- **❌ Mapas com divergências:** {total_issues} ({total_issues/total_files*100:.1f}%)\n\n")

        total_produtos_validados = sum(m["total_produtos"] for m in mapas_ok)
        f.write(f"**Total de produtos validados:** {total_produtos_validados}\n\n")
        f.write("| # | Mapa | Produtos | Status |\n")
        f.write("|---|------|----------|--------|\n")
        for idx, mapa_info in enumerate(sorted(mapas_ok, key=lambda x: x["mapa"]), 1):
            f.write(f"| {idx} | {mapa_info['mapa']} | {mapa_info['total_produtos']} | ✅ Validado |\n")

        f.write("\n## ❌ Mapas com divergências\n\n")
        if not mapas_com_divergencias:
            f.write("Nenhum.\n")
        else:
            for mapa in mapas_com_divergencias:
                f.write(f"- **Mapa {mapa['mapa']}**\n")
                for issue in mapa["issues"]:
                    f.write(f"  - {issue}\n")
                f.write("\n")

    print(f"Relatório salvo: {report_path}")


def main():
    base_dir = Path("/mnt/c/prd_debian")
    txt_dir = base_dir / "mapas/out"
    xml_dirs = [
        base_dir / "mapas_xml_saidas",
        base_dir / "mapas_xml_saidas_filtrados",
        base_dir / "meus_xmls",
    ]

    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║        VALIDAÇÃO CRUZADA: TXTs vs XMLs Originais             ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

    txt_files = list(txt_dir.glob("*.txt"))
    print(f"📊 TXTs para validar: {len(txt_files)}")
    print()

    total_ok = 0
    total_issues = 0
    total_not_found = 0

    mapas_ok = []
    mapas_com_divergencias = []

    for txt_file in sorted(txt_files):
        mapa_num = extract_mapa_number(txt_file.name)

        if not mapa_num:
            print(f"⚠️  {txt_file.name}: Não foi possível extrair número do mapa")
            total_not_found += 1
            continue

        xml_file = None
        for xml_dir in xml_dirs:
            candidates = list(xml_dir.glob(f"*{mapa_num}*.xml"))
            if candidates:
                xml_file = candidates[0]
                break

        if not xml_file:
            print(f"⚠️  Mapa {mapa_num}: XML não encontrado")
            total_not_found += 1
            continue

        xml_products = parse_xml_quantities(xml_file)
        txt_products = parse_txt_quantities(txt_file)

        if not xml_products:
            print(f"⚠️  Mapa {mapa_num}: XML vazio ou erro ao ler")
            total_issues += 1
            continue

        if not txt_products:
            print(f"⚠️  Mapa {mapa_num}: TXT vazio ou erro ao ler")
            total_issues += 1
            continue

        issues = compare_products(xml_products, txt_products)

        if issues:
            print(f"✖ Mapa {mapa_num}: {len(issues)} problema(s)")
            for issue in issues:
                print(issue)
            print()
            total_issues += 1
            mapas_com_divergencias.append(
                {
                    "mapa": mapa_num,
                    "issues": issues,
                    "total_produtos_xml": len(xml_products),
                    "total_produtos_txt": len(txt_products),
                }
            )
        else:
            total_ok += 1
            mapas_ok.append({"mapa": mapa_num, "total_produtos": len(xml_products)})

    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                       RESUMO DA VALIDAÇÃO                     ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(f"✅ Mapas OK (produtos batem):        {total_ok}")
    print(f"❌ Mapas com problemas:              {total_issues}")
    print(f"⚠️  XMLs não encontrados:             {total_not_found}")
    print(f"📊 Total processado:                 {len(txt_files)}")
    print()

    if total_ok == len(txt_files):
        print("🎉 PERFEITO! Todos os TXTs batem com os XMLs!")
    elif total_issues == 0 and total_not_found > 0:
        print("✅ Todos os TXTs validados batem com os XMLs encontrados.")
    else:
        print(f"⚠️  Atenção: {total_issues} mapas com divergências")

    print()
    print("📝 Gerando relatório detalhado em markdown...")
    generate_markdown_report(
        mapas_ok, mapas_com_divergencias, total_ok, total_issues, total_not_found, len(txt_files)
    )


if __name__ == "__main__":
    main()
