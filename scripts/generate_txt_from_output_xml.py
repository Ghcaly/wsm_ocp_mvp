from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET

# Resolve paths relative to repository root (parent of scripts folder)
REPO_ROOT = Path(__file__).resolve().parent.parent
output_xml = REPO_ROOT / 'mapas_xml_saidas' / '0d1deab1a8b44a43b4048212edbb13a1_ocp_622704_0764_20251218000220.xml'
out_txt = REPO_ROOT / 'mapas' / 'out' / 'palletize_result_map_622704_fixed.txt'

if not output_xml.exists():
    print('Output XML not found:', output_xml)
    raise SystemExit(1)

# parse
tree = ET.parse(output_xml)
root = tree.getroot()

counter = Counter()

# simpler approach: iterate over item nodes
for item in root.findall('.//item'):
    cd = item.find('cdItem')
    qty = item.find('qtUnVenda')
    if qty is None:
        qty = item.find('qtUn')
    if cd is not None and cd.text:
        code = cd.text.strip()
        q = 0
        if qty is not None and qty.text:
            try:
                q = int(qty.text.strip())
            except Exception:
                try:
                    q = int(float(qty.text.strip()))
                except Exception:
                    q = 0
        counter[code] += q

# write TXT
with out_txt.open('w', encoding='utf-8') as f:
    f.write(f"Mapa: 622704\n")
    f.write(f"Produtos únicos: {len(counter)}\n")
    f.write('\n')
    f.write('Codigo;Quantidade\n')
    for code, qty in sorted(counter.items(), key=lambda x: int(x[0])):
        f.write(f"{code};{qty}\n")

print('Generated', out_txt)
