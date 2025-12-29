#!/usr/bin/env python3
"""
Script de comparação entre XML de saída ORTEC e TXT gerado
"""
import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import sys

def parse_xml(xml_file):
    """Extrai dados do XML ORTEC"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    pallets = {}
    total = 0
    skus = defaultdict(int)
    
    for pallet in root.findall('.//pallet'):
        lado = pallet.find('cdLado').text
        baia = pallet.find('nrBaiaGaveta').text
        pallet_key = f"P0{baia}_{lado}_0{baia}"
        
        items_dict = defaultdict(int)
        for item in pallet.findall('.//item'):
            cd_item = item.find('cdItem').text
            qt_venda = int(item.find('qtUnVenda').text)
            qt_avulsa = int(item.find('qtUnAvulsa').text)
            qtd = qt_venda + qt_avulsa
            items_dict[cd_item] += qtd
            skus[cd_item] += qtd
            total += qtd
        
        pallets[pallet_key] = dict(items_dict)
    
    return pallets, dict(skus), total

def parse_txt(txt_file):
    """Extrai dados do TXT gerado"""
    pallets = {}
    total = 0
    skus = defaultdict(int)
    fora_caminhao = defaultdict(int)
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        current_pallet = None
        in_fora_section = False
        
        for line in lines:
            # Detecta pallet
            if re.match(r'^P\d{2}_[AM]_\d{2}_', line):
                match = re.match(r'^(P\d{2}_[AM]_\d{2})_', line)
                if match:
                    current_pallet = match.group(1)
                    pallets[current_pallet] = defaultdict(int)
                    in_fora_section = False
            
            # Detecta seção "fora do caminhão"
            elif 'fora do caminhão' in line.lower():
                in_fora_section = True
                current_pallet = None
            
            # Linha de produto dentro de pallet
            elif current_pallet and line.strip().startswith('| 0'):
                try:
                    cleaned = line.replace('|', '').strip()
                    match = re.search(r'0\s+(\d+)\s+.*?\s+(\d+)\s+\d{4}\s+\d+/\d+', cleaned)
                    
                    if match:
                        sku = match.group(1)
                        qtd = int(match.group(2))
                        pallets[current_pallet][sku] += qtd
                        skus[sku] += qtd
                        total += qtd
                except:
                    pass
            
            # Linha de produto fora do caminhão
            elif in_fora_section and line.strip().startswith('|') and not line.strip().startswith('|---'):
                try:
                    cleaned = line.replace('|', '').strip()
                    match = re.search(r'(\d+)\s+.*?\s+(\d+)\s+\d{4}\s+\d+/\d+', cleaned)
                    
                    if match:
                        sku = match.group(1)
                        qtd = int(match.group(2))
                        fora_caminhao[sku] += qtd
                        skus[sku] += qtd
                        total += qtd
                except:
                    pass
    
    # Converter defaultdict para dict
    for key in pallets:
        pallets[key] = dict(pallets[key])
    
    return pallets, dict(skus), total, dict(fora_caminhao)

def gerar_relatorio(xml_file, txt_file):
    """Gera relatório completo de comparação"""
    
    # Parse dos arquivos
    xml_pallets, xml_skus, xml_total = parse_xml(xml_file)
    txt_pallets, txt_skus, txt_total, txt_fora = parse_txt(txt_file)
    
    # Extrai número do mapa
    mapa_num = re.search(r'mapa_(\d+)', xml_file)
    mapa_num = mapa_num.group(1) if mapa_num else "N/A"
    
    print("\n" + "="*100)
    print(f"📊 RELATÓRIO DE COMPARAÇÃO: XML ORTEC vs TXT GERADO - Mapa {mapa_num}")
    print("="*100)
    
    # Resumo quantitativo
    print(f"\n📦 RESUMO GERAL:")
    print(f"{'':25} {'XML':>12} {'TXT':>12} {'Diferença':>15}")
    print("-" * 100)
    print(f"{'Pallets':25} {len(xml_pallets):>12} {len(txt_pallets):>12} {len(txt_pallets)-len(xml_pallets):>15}")
    print(f"{'Unidades Total':25} {xml_total:>12} {txt_total:>12} {txt_total-xml_total:>+15}")
    print(f"{'SKUs Únicos':25} {len(xml_skus):>12} {len(txt_skus):>12} {len(txt_skus)-len(xml_skus):>+15}")
    if txt_fora:
        print(f"{'Produtos fora caminhão':25} {'-':>12} {len(txt_fora):>12} {''}")
        print(f"{'Un. fora caminhão':25} {'-':>12} {sum(txt_fora.values()):>12} {''}")
    
    # Comparação por pallet
    print(f"\n🔍 COMPARAÇÃO POR PALLET:")
    print("-" * 100)
    print(f"{'Pallet':15} {'SKUs':>8} {'':3} {'SKUs':>8} {'Un.':>10} {'':3} {'Un.':>10} {'Status':>15}")
    print(f"{'':15} {'XML':>8} {'':3} {'TXT':>8} {'XML':>10} {'':3} {'TXT':>10} {''}")
    print("-" * 100)
    
    match_pallets = 0
    total_sku_checks = 0
    total_sku_matches = 0
    
    for pallet_id in sorted(xml_pallets.keys()):
        xml_items = xml_pallets[pallet_id]
        txt_items = txt_pallets.get(pallet_id, {})
        
        xml_sum = sum(xml_items.values())
        txt_sum = sum(txt_items.values())
        
        all_skus = set(xml_items.keys()) | set(txt_items.keys())
        matches = sum(1 for sku in all_skus if xml_items.get(sku, 0) == txt_items.get(sku, 0))
        
        total_sku_checks += len(all_skus)
        total_sku_matches += matches
        
        is_match = (xml_sum == txt_sum and matches == len(all_skus))
        if is_match:
            match_pallets += 1
            status = "✅ MATCH"
        else:
            status = "❌ DIFF"
        
        print(f"{pallet_id:15} {len(xml_items):>8} {'→':>3} {len(txt_items):>8} {xml_sum:>10} {'→':>3} {txt_sum:>10} {status:>15}")
    
    # Análise de SKUs
    print(f"\n📝 ANÁLISE DE SKUs:")
    print("-" * 100)
    
    all_skus = set(xml_skus.keys()) | set(txt_skus.keys())
    matches = []
    diffs = []
    
    for sku in sorted(all_skus):
        xml_qty = xml_skus.get(sku, 0)
        txt_qty = txt_skus.get(sku, 0)
        
        if xml_qty == txt_qty:
            matches.append(sku)
        else:
            diff = txt_qty - xml_qty
            diffs.append((sku, xml_qty, txt_qty, diff, sku in txt_fora))
    
    print(f"\n✅ SKUs Idênticos: {len(matches)}/{len(all_skus)}")
    
    if diffs:
        print(f"\n❌ SKUs com Diferenças: {len(diffs)}/{len(all_skus)}")
        print(f"\n{'SKU':>8} {'XML':>8} {'TXT':>8} {'Diff':>10} {'Observação':>20}")
        print("-" * 100)
        
        for sku, xml_qty, txt_qty, diff, is_fora in diffs[:25]:
            obs = ""
            if is_fora:
                obs = "🚫 Fora do caminhão"
            elif xml_qty == 0:
                obs = "⚠️  Só no TXT"
            elif txt_qty == 0:
                obs = "⚠️  Só no XML"
            else:
                obs = "❌ Divergente"
            
            print(f"{sku:>8} {xml_qty:>8} {txt_qty:>8} {diff:>+10} {obs:>20}")
        
        if len(diffs) > 25:
            print(f"\n... e mais {len(diffs)-25} diferenças")
    
    # Resultado final
    print("\n" + "="*100)
    print("📈 RESULTADO FINAL:")
    print("-" * 100)
    
    pallet_acc = (match_pallets / len(xml_pallets) * 100) if xml_pallets else 0
    sku_acc = (total_sku_matches / total_sku_checks * 100) if total_sku_checks else 0
    unit_diff_pct = ((txt_total - xml_total) / xml_total * 100) if xml_total else 0
    
    print(f"✓ Pallets Corretos: {match_pallets}/{len(xml_pallets)} ({pallet_acc:.1f}%)")
    print(f"✓ SKUs Corretos: {total_sku_matches}/{total_sku_checks} ({sku_acc:.1f}%)")
    print(f"✓ SKUs Idênticos: {len(matches)}/{len(all_skus)} ({len(matches)/len(all_skus)*100:.1f}%)")
    print(f"⚠  Diferença de Unidades: {txt_total - xml_total:+d} ({unit_diff_pct:+.2f}%)")
    
    print("\n" + "="*100)
    if match_pallets == len(xml_pallets) and len(diffs) == 0:
        print("🎉🎉🎉 PERFEITO! XML E TXT SÃO 100% IDÊNTICOS! 🎉🎉🎉")
    elif sku_acc >= 95:
        print(f"✅ EXCELENTE! Precisão de {sku_acc:.1f}%")
    elif sku_acc >= 80:
        print(f"✅ BOM! Precisão de {sku_acc:.1f}% - Pequenas divergências")
    else:
        print(f"⚠️  ATENÇÃO! Precisão de {sku_acc:.1f}% - Revisar processamento")
    print("="*100 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python comparar_xml_txt.py <arquivo_xml> <arquivo_txt>")
        sys.exit(1)
    
    gerar_relatorio(sys.argv[1], sys.argv[2])
