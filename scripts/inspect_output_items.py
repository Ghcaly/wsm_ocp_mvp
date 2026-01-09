import xml.etree.ElementTree as ET
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
p = REPO_ROOT / 'mapas_xml_saidas' / '0d1deab1a8b44a43b4048212edbb13a1_ocp_622704_0764_20251218000220.xml'
root=ET.parse(p).getroot()
for i,item in enumerate(root.findall('.//item')):
    cd=item.find('cdItem')
    q=item.find('qtUnVenda')
    print(i, cd.text if cd is not None else None, q.text if q is not None else None)
    if i>40:
        break
