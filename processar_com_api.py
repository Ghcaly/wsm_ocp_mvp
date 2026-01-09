#!/usr/bin/env python3
"""
Processa XMLs usando a API do WMS Converter
"""
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configurações
API_URL = "http://localhost:8000/convert"
XML_INPUT_DIR = Path("C:/mapas_xml_saidas/last_5_days")
OUTPUT_DIR = Path("C:/prd_debian/txts_gerados")
CONCURRENCY = 4

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def processar_xml(xml_file):
    """Processa um XML via API e salva o TXT"""
    try:
        with open(xml_file, 'rb') as f:
            files = {'file': (xml_file.name, f, 'application/xml')}
            response = requests.post(API_URL, files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            # Salvar TXT se existir
            if 'txt' in result and result['txt']:
                txt_file = OUTPUT_DIR / f"{xml_file.stem}.txt"
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(result['txt'])
                return (xml_file.name, True, f"TXT gerado: {txt_file.name}")
            else:
                return (xml_file.name, False, "Sem TXT na resposta")
        else:
            return (xml_file.name, False, f"HTTP {response.status_code}: {response.text[:100]}")
    
    except Exception as e:
        return (xml_file.name, False, str(e)[:100])

def main():
    # Listar XMLs
    xmls = list(XML_INPUT_DIR.glob("*.xml"))
    if not xmls:
        print(f"Nenhum XML encontrado em {XML_INPUT_DIR}")
        return
    
    print(f"Encontrados {len(xmls)} arquivos XML")
    print(f"API: {API_URL}")
    print(f"Output: {OUTPUT_DIR}\n")
    
    # Testar API
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        if health.status_code != 200:
            print("❌ API não está respondendo!")
            return
        print("✅ API online\n")
    except:
        print("❌ API não está acessível em http://localhost:8000")
        return
    
    # Processar em paralelo
    sucesso = 0
    erros = 0
    erros_list = []
    
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = {executor.submit(processar_xml, xml): xml for xml in xmls}
        
        for i, future in enumerate(as_completed(futures), 1):
            filename, ok, msg = future.result()
            
            if ok:
                sucesso += 1
            else:
                erros += 1
                erros_list.append((filename, msg))
            
            if i % 100 == 0:
                print(f"Progresso: {i}/{len(xmls)} ({sucesso} OK, {erros} erros)")
    
    elapsed = time.time() - start
    
    print(f"\n{'='*70}")
    print(f"PROCESSAMENTO CONCLUÍDO")
    print(f"{'='*70}")
    print(f"Total: {len(xmls)} arquivos")
    print(f"Sucesso: {sucesso} ({sucesso/len(xmls)*100:.1f}%)")
    print(f"Erros: {erros} ({erros/len(xmls)*100:.1f}%)")
    print(f"Tempo: {elapsed:.1f}s ({len(xmls)/elapsed:.1f} arquivos/seg)")
    print(f"TXTs salvos em: {OUTPUT_DIR}")
    
    if erros_list and erros <= 20:
        print(f"\nErros:")
        for filename, msg in erros_list:
            print(f"  - {filename}: {msg}")

if __name__ == "__main__":
    main()
