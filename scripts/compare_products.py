import re
import xml.etree.ElementTree as ET
from pathlib import Path

xml_path = Path('meus_xmls/0d1deab1a8b44a43b4048212edbb13a1_m_mapa_622704_0764_20251217210326.xml')
txt_path = Path('mapas/out/palletize_result_map_622704.txt')

# parse xml
xml_codes = []
if xml_path.exists():
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for cd in root.findall('.//cdItem'):
        code = cd.text.strip()
        xml_codes.append(code)

# parse txt
txt_codes = []
if txt_path.exists():
    txt = txt_path.read_text(encoding='utf-8')
    for m in re.finditer(r"\|\s*\d+\s+(\d+)\s+", txt):
        txt_codes.append(m.group(1))

xml_set = set(xml_codes)
txt_set = set(txt_codes)

only_in_xml = sorted(xml_set - txt_set, key=int)
only_in_txt = sorted(txt_set - xml_set, key=int)

print(f"XML codes count (unique): {len(xml_set)}\nTXT codes count (unique): {len(txt_set)}")
print()
print(f"Only in XML ({len(only_in_xml)}): {only_in_xml[:50]}")
print()
print(f"Only in TXT ({len(only_in_txt)}): {only_in_txt[:50]}")

# show example lines from TXT for first 10 codes present in TXT
print()
print('Exemplos de linhas do TXT para alguns códigos:')
if txt_path.exists():
    lines = txt.splitlines()
    for code in list(sorted(txt_set, key=int))[:20]:
        for ln in lines:
            if re.search(rf"\b{code}\b", ln):
                print(code + ': ' + ln.strip())
                break

# totals occurrences in xml
from collections import Counter
xml_counter = Counter(xml_codes)
print()
print('Top 10 produtos mais frequentes no XML:')
for code, cnt in xml_counter.most_common(10):
    print(code, cnt)

# exit
