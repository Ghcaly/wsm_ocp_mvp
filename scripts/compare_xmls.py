import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

input_xml = Path('meus_xmls/0d1deab1a8b44a43b4048212edbb13a1_m_mapa_622704_0764_20251217210326.xml')
output_xml = Path('mapas_xml_saidas/0d1deab1a8b44a43b4048212edbb13a1_ocp_622704_0764_20251218000220.xml')

def extract_codes_and_qty(path, tag_item='cdItem', qty_tag='qtUn'):
    codes = []
    qtys = Counter()
    if not path.exists():
        return codes, qtys
    tree = ET.parse(path)
    root = tree.getroot()
    for cd in root.findall('.//'+tag_item):
        code = cd.text.strip()
        # find qty sibling
        parent = cd.getparent() if hasattr(cd, 'getparent') else None
        # simpler: search for qty within parent node
        # get parent via traversal
        if code:
            codes.append(code)
    # qty: fallback parse all qty_tag values
    for q in root.findall('.//'+qty_tag):
        try:
            val = int(q.text.strip())
            # find nearest cdItem ancestor sibling - this is approximate
            # we'll just count qtys by sequence
            qtys_total = qtys  # placeholder
        except Exception:
            pass
    return codes, qtys

# For this comparison we only need unique codes sets

def codes_set(path, tag='cdItem'):
    if not path.exists():
        return set()
    tree = ET.parse(path)
    root = tree.getroot()
    return set([c.text.strip() for c in root.findall('.//'+tag) if c.text and c.text.strip()])

in_set = codes_set(input_xml, 'cdItem')
out_set = codes_set(output_xml, 'cdItem')

only_in_input = sorted(in_set - out_set, key=int)
only_in_output = sorted(out_set - in_set, key=int)

print(f"Input unique codes: {len(in_set)}")
print(f"Output unique codes: {len(out_set)}")
print()
print(f"Only in input ({len(only_in_input)}): {only_in_input}")
print()
print(f"Only in output ({len(only_in_output)}): {only_in_output}")
