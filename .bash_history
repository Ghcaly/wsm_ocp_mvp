exit
sudo apt install git
git --version
sudo apt install git 
run apt-get update
sudo apt update
clear
sudo apt install git 
clear
ls
mkdir ocp_wms_core
ls
cd ./ocp_wms_core/
clear
code .
ls
cd ..
cd..
cd ..
cd..
cd ..
clear
ls
cd c/
ls
cd ..
clear
cd wsl
ls
cd ..
ls
cd wsl
exit
clear
ls
cd wms_converter/
clear
]ls
ls
clear
ls
cd ..
clear
ls
exit
cd /home/prd_debian/wms_converter && pip install -r requirements.txt
cd /home/prd_debian/wms_converter && python3 -m venv venv
cd /home/prd_debian/wms_converter && source venv/bin/activate && pip install -r requirements.txt
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/main.py
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/simple_main.py
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/run_palletization.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && pip install -q flask flask-cors 2>&1 | tail -5
cd /home/prd_debian/ocp_wms_core/ocp_score-main && pip install flask flask-cors requests
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && pip install flask flask-cors requests
ls
cd..
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python api_server.py
sudo apt install python-venv
clear
pip3 install python3
pip3 install python-venv
clear
python3 -m venv wms_ven
clear
python --version
python
clear
sudo apt install python
sudo apt install python3
clear
python3 -m venv wms_ven
python3
clear
pip --version
sudo apt install pip
clear
pip --version
clear
pip3 install python-venv
clear
ls
clear
source ./wms_ven/bin/actavate
clear
python -m venv wms_venv
pytho3n -m venv wms_venv
python3 -m venv wms_venv
clear
python3 -m venv wms_venv
sudo apt install python3.13-venv
clear
python3 -m venv wms_venv
clear
source ./wms_venv/bin/activate
clear
git --version
clear
sudo apt install zip
clear
ls
unzip ./ocp_score-main.zip
clear
cd ..
mkdir mapas
cd ./mapas/
mkdir in
mkdir out
ls
cd ..
ls
mkdir wms_converter
ls
cd ./wms_converter/
clear
code .
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python ocp_score-main/simple_api.py
sleep 2 && curl -s http://localhost:5000/health | python3 -m json.tool
curl -s http://localhost:5000/health
sleep 5 && curl -s http://localhost:5000/health
ps aux | grep -E "(python|flask)" | grep -v grep | head -5
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && nohup python ocp_score-main/simple_api.py > /tmp/api.log 2>&1 &
sleep 3 && curl -s http://localhost:5000/health
curl -s http://localhost:5000/mapas/list | python3 -m json.tool
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/restart_api.sh
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/check_api.sh && cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./check_api.sh
curl -X POST http://localhost:5000/mapas/process-auto   -H 'Content-Type: application/json'   -d '{"format":"txt"}'
clear
curl -X POST http://localhost:5000/mapas/process-auto -H 'Content-Type: application/json' -d '{"format":"txt"}'
curl -X POST 'http://localhost:5000/mapas/process-auto' -H 'Content-Type: application/json' -d '{"format":"txt"}'
curl -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=txt'
sleep 2 && curl -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=txt'
curl -s -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json' | python3 -m json.tool
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./restart_api.sh
ls -lah /home/prd_debian/mapas/out/
curl -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=txt'
ls -lah /home/prd_debian/mapas/out/
cat /home/prd_debian/mapas/out/config_completo_result_20251221_195237.txt
curl -s -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=json' | python3 -m json.tool | head -30
ls -lh /home/prd_debian/mapas/out/
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./restart_api.sh
curl -s http://localhost:5000/mapas/outputs | python3 -m json.tool
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./restart_api.sh
rm /home/prd_debian/mapas/out/* 2>/dev/null; curl -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=txt' | head -20
tail -30 /tmp/api.log
ls -la /home/prd_debian/ocp_wms_core/ocp_score-main/__init__.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./restart_api.sh
rm /home/prd_debian/mapas/out/* 2>/dev/null; curl -s -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=txt' | head -30
tail -40 /tmp/api.log | grep -A 5 "Módulos não disponíveis"
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./restart_api.sh
curl -s -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=txt' | head -30
tail -50 /tmp/api.log | grep -B 5 -A 10 "Módulos não disponíveis"
tail -100 /tmp/api.log 2>&1 | strings | grep -A 5 "Módulos não disponíveis"
python3 -c "with open('/tmp/api.log', 'rb') as f: lines = f.readlines(); print(''.join([l.decode('utf-8', errors='replace') for l in lines[-50:]]))"
cd /home/prd_debian/ocp_wms_core/ocp_score-main && python3 <<'EOF'
import sys
sys.path.insert(0, '/home/prd_debian/ocp_wms_core/ocp_score-main')
try:
    from service.calculator_palletizing_service import CalculatorPalletizingService
    from domain.context import Context
    print("SUCCESS: Imports funcionaram")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
EOF

cd /home/prd_debian/ocp_wms_core/ocp_score-main && python3 test_imports.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Testa o import que está falhando
try:
    from service.calculator_palletizing_service import CalculatorPalletizingService
    print('SUCCESS: Import funcionou!')
except ImportError as e:
    print(f'ERRO: {e}')
    print('\\nVamos ver onde está o problema:')
    
    # Testa imports individuais
    try:
        from service import calculator_palletizing_service
        print('  - service.calculator_palletizing_service: OK')
    except Exception as e2:
        print(f'  - service.calculator_palletizing_service: FALHOU - {e2}')
"
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/process_mapas.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python process_mapas.py --auto
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && pip install pandas
cd /home/prd_debian/ocp_wms_core/ocp_score-main && python process_mapas.py --auto 2>&1 | head -100
ls -la /home/prd_debian/ocp_wms_core/ocp_score-main/*.py | head -20
cd /home/prd_debian/ocp_wms_core/ocp_score-main && python run_palletization.py --help
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/generate_txt.py && cd /home/prd_debian/ocp_wms_core/ocp_score-main && python generate_txt.py /home/prd_debian/mapas/in/config_completo.json /home/prd_debian/mapas/in/inputcompleto.json 2>&1 | head -100
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/json_to_txt.py && cd /home/prd_debian/ocp_wms_core/ocp_score-main && python json_to_txt.py --auto
cat /home/prd_debian/mapas/out/inputcompleto_report.txt
cd /home/prd_debian/ocp_wms_core && python3 -m ocp_score-main.service.palletizing_processor 2>&1 | head -20
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && pip install multipledispatch
cd /home/prd_debian/ocp_wms_core && python3 -m ocp_score-main.service.palletizing_processor 2>&1 | head -30
chmod +x /home/prd_debian/ocp_wms_core/process_palletization.py && cd /home/prd_debian/ocp_wms_core && python3 process_palletization.py 2>&1 | head -80
chmod +x /home/prd_debian/ocp_wms_core/GERAR_TXT.sh && /home/prd_debian/ocp_wms_core/GERAR_TXT.sh 2>&1 | head -100
chmod +x /home/prd_debian/ocp_wms_core/GERAR_TXT_SIMPLES.sh && /home/prd_debian/ocp_wms_core/GERAR_TXT_SIMPLES.sh 2>&1 | head -150
# Cria diretório
mkdir -p /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768
# Copia arquivos
cp /home/prd_debian/mapas/in/config_completo.json /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/config.json
cp /home/prd_debian/mapas/in/inputcompleto.json /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/input.json
echo "✓ Arquivos copiados para data/route/620768/"
ls -la /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/
mkdir -p /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768 && cp /home/prd_debian/mapas/in/config_completo.json /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/config.json && cp /home/prd_debian/mapas/in/inputcompleto.json /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/input.json && ls -la /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/
cd /home/prd_debian/ocp_wms_core && python3 -m ocp_score-main.service.palletizing_processor 2>&1 | head -200
find /home/prd_debian/ocp_wms_core -name "*.csv" -type f 2>/dev/null
mkdir -p /home/prd_debian/ocp_wms_core/ocp_score-main/data && cp /home/prd_debian/ocp_wms_core/ocp_score-main/database/itens.csv /home/prd_debian/ocp_wms_core/ocp_score-main/data/csv-itens_17122025.csv && ls -lh /home/prd_debian/ocp_wms_core/ocp_score-main/data/*.csv
cd /home/prd_debian/ocp_wms_core && timeout 60 python3 -m ocp_score-main.service.palletizing_processor 2>&1 | tail -50
ls -lh /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/output/
cat /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/output/palletize_result_map_620815.txt
cp /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768/output/palletize_result_map_620815.txt /home/prd_debian/mapas/out/ && ls -lh /home/prd_debian/mapas/out/*.txt
chmod +x /home/prd_debian/ocp_wms_core/GERAR_TXT_COMPLETO.sh && ls -la /home/prd_debian/ocp_wms_core/*.sh
ps aux | grep simple_api.py | grep -v grep
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./restart_api.sh
curl -s http://localhost:5000/ | python3 -m json.tool | head -30
curl -s http://localhost:5000/health | python3 -m json.tool
curl -s http://localhost:5000/mapas/list | python3 -m json.tool
curl -s http://localhost:5000/mapas/outputs | python3 -m json.tool
curl -s -X POST 'http://localhost:5000/mapas/process/config_completo.json?data_file=inputcompleto.json&format=json' | python3 -m json.tool | head -40
ls -lh /home/prd_debian/mapas/out/*.json 2>/dev/null | tail -3
curl -s -X POST http://localhost:5000/mapas/process-auto -H 'Content-Type: application/json' -d '{"format":"json"}' | python3 -m json.tool | head -25
ls -lh /home/prd_debian/mapas/out/
cd /home/prd_debian/mapas/out && rm -f config_completo_result_*.txt config_completo_result_*.json inputcompleto_report.txt && ls -lh
cd /home/prd_debian/ocp_wms_core/ocp_score-main && rm -f test_imports.py json_to_txt.py process_mapas.py generate_txt.py && ls -la *.py 2>/dev/null | grep -E "(test|json_to|process_mapas|generate)" || echo "✓ Arquivos de teste removidos"
cd /home/prd_debian/ocp_wms_core && rm -f GERAR_TXT.sh GERAR_TXT_SIMPLES.sh run_api.py && ls -la *.sh *.py 2>/dev/null | head -20
cd /home/prd_debian/ocp_wms_core && rm -f process_palletization.py start_api.py && ls -la *.sh *.py *.md 2>/dev/null
cd /home/prd_debian/ocp_wms_core && rm -f COMO_GERAR_TXT_COMPLETO.md && mv README_TXT_COMPLETO.md README_GERACAO_TXT.md && ls -la *.md *.sh
cd /home/prd_debian/ocp_wms_core/ocp_score-main && rm -f FORMATO_TXT.md test_files_endpoint.sh test_mapas.sh COMANDOS_RAPIDOS.md GUIA_RAPIDO.md README_MAPAS.md USAGE.md 2>/dev/null; ls -la *.md *.sh 2>/dev/null | grep -v check_api || echo "✓ Limpeza concluída"
cd /home/prd_debian/ocp_wms_core/ocp_score-main && rm -f start_api.sh check_api.sh && echo "✓ Scripts de teste removidos" && ls -la *.sh
cd /home/prd_debian/ocp_wms_core/ocp_score-main && find . -name "*.pyc" -o -name "__pycache__" -o -name "*.log" -o -name "nohup.out" 2>/dev/null | head -10
cd /home/prd_debian/ocp_wms_core/ocp_score-main && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; find . -name "*.pyc" -delete 2>/dev/null; echo "✓ Cache Python limpo"
echo "📁 Estrutura Final Organizada:" && echo "" && echo "=== Diretório Principal ===" && ls -lh /home/prd_debian/ocp_wms_core/*.{sh,md} 2>/dev/null && echo "" && echo "=== API ===" && ls -lh /home/prd_debian/ocp_wms_core/ocp_score-main/*.sh 2>/dev/null && echo "" && echo "=== Arquivos de Saída ===" && ls -lh /home/prd_debian/mapas/out/
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ls -la test*.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && rm -f test_api.py test_files_api.py test_mapas.py && echo "✓ Arquivos de teste removidos" && ls -la *.py | grep -E "simple_api|api_server|run_palletization"
cd /home/prd_debian/ocp_wms_core/ocp_score-main && find . -maxdepth 1 -name "*.sh" -ls 2>/dev/null
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ls -la *.md 2>/dev/null
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ls -la reports/ 2>/dev/null | head -20
cd /home/prd_debian/ocp_wms_core/ocp_score-main/reports && rm -f *.md && ls -la
ls -la /tmp/api.log /tmp/*.py 2>/dev/null | head -5
rm -f /tmp/process_temp.py /tmp/run_paletizacao.py && echo "✓ Scripts temporários removidos" && echo "" && echo "📊 Resumo Final:" && echo "  ✓ Arquivos de teste Python removidos" && echo "  ✓ Relatórios de teste antigos removidos" && echo "  ✓ Scripts temporários removidos" && echo "  ✓ Log da API mantido: /tmp/api.log"
echo "📁 Estrutura Final Limpa:" && echo "" && echo "=== Scripts Principais ===" && ls -lh /home/prd_debian/ocp_wms_core/*.sh && echo "" && echo "=== Documentação ===" && ls -lh /home/prd_debian/ocp_wms_core/*.md && echo "" && echo "=== API ===" && ls -lh /home/prd_debian/ocp_wms_core/ocp_score-main/simple_api.py /home/prd_debian/ocp_wms_core/ocp_score-main/restart_api.sh
ps aux | grep simple_api.py | grep -v grep
cd /home/prd_debian/ocp_wms_core/ocp_score-main && ./restart_api.sh 2>&1 | tail -15
clear
git branch 
cd ..
git branch 
cd ..
git status
cd ./ocp_wms_core/
clear
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python test_config_generator.py
clear
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python ocp_score-main/simple_api.py
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/test_files_endpoint.sh /home/prd_debian/ocp_wms_core/ocp_score-main/test_files_api.py
python test_files_api.py config.json data.json --format txt
mkdir -p /home/prd_debian/mapas/in && ls -la /home/prd_debian/mapas/
mkdir -p /home/prd_debian/mapas/in && echo "✓ Pasta criada" && ls -la /home/prd_debian/mapas/
chmod +x /home/prd_debian/ocp_wms_core/ocp_score-main/test_mapas.sh /home/prd_debian/ocp_wms_core/ocp_score-main/test_mapas.py
curl -X POST http://localhost:5000/mapas/process-auto   -H 'Content-Type: application/json'   -d '{"format":"txt"}'
ps aux | grep simple_api.py | grep -v grep
cd /home/prd_debian/ocp_wms_core && chmod +x start_api.py && source wms_venv/bin/activate && PYTHONPATH=/home/prd_debian/ocp_wms_core python start_api.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python api_server.py
cd /home/prd_debian/ocp_wms_core && ls -la | grep ocp
cd /home/prd_debian/wms_converter && nohup ./process_all.sh > /tmp/process_all.log 2>&1 &
sleep 30 && ls -1 /home/prd_debian/mapas/in/json/*.json 2>/dev/null | wc -l
cat /home/prd_debian/mapas/in/json/input_621622.json | python3 -m json.tool | head -35
clear
tail -10 /tmp/process_all.log
clear
ps aux | grep "python api.py" | grep -v grep
netstat -tuln | grep 8000
ss -tuln | grep 8000
tail -5 /home/prd_debian/wms_converter/api.py
hostname -I | awk '{print $1}'
curl -s http://172.24.26.161:8000/health
ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
cp /home/prd_debian/wms_converter/expose_api.ps1 /mnt/c/Users/ 2>/dev/null || echo "Script criado em: /home/prd_debian/wms_converter/expose_api.ps1"
cd /home/prd_debian/wms_converter && rm -f expose_port.txt expose_api.ps1 client.py process.py && echo "Arquivos removidos"
cd /home/prd_debian/wms_converter && ls -la
cd /home/prd_debian/wms_converter && rm -f .env.example && ls -la modules/
cd /home/prd_debian/wms_converter && source venv/bin/activate && python api.py
cd /home/prd_debian/wms_converter && source venv/bin/activate && python process.py
cd /home/prd_debian/wms_converter && source venv/bin/activate && pip install requests && python process.py
clear
cd /home/prd_debian/wms_converter && source venv/bin/activate && python api.py
sleep 2 && /home/prd_debian/wms_converter/convert_map.sh
cat /home/prd_debian/mapas/in/xml/xml_620807_resposta.xml
find /home/prd_debian/mapas -name "*.xml" -type f 2>/dev/null
head -100 /home/prd_debian/mapas/in/xml/0a4854c0cf174ef5bc88cd6fefb27978_m_mapa_622503_0764_20251215205433.xml
pkill -f "python api.py" && sleep 1
cd /home/prd_debian/wms_converter && source venv/bin/activate && python api.py &
sleep 3 && cd /home/prd_debian/wms_converter && source venv/bin/activate && python process.py
chmod +x /home/prd_debian/wms_converter/convert_map.sh && /home/prd_debian/wms_converter/convert_map.sh
/home/prd_debian/wms_converter/convert_map.sh
curl -s http://localhost:8000/health
curl -s -X POST "http://localhost:8000/convert" -F "file=@/home/prd_debian/mapas/in/xml/xml_620807_requisicao.xml" -o /tmp/result.json && cat /tmp/result.json | head -20
ls -la /home/prd_debian/mapas/in/xml/
/home/prd_debian/wms_converter/convert_map.sh
cat /home/prd_debian/mapas/in/json/input_UNKNOWN.json | head -30
head -50 /home/prd_debian/mapas/in/xml/xml_620807_resposta.xml
/home/prd_debian/wms_converter/convert_map.sh
pkill -f "python api.py"
cd /home/prd_debian/wms_converter && source venv/bin/activate && nohup python api.py > /tmp/api.log 2>&1 &
pkill -f "python api.py" && sleep 1 && cd /home/prd_debian/wms_converter && source venv/bin/activate && python api.py &
sleep 2 && /home/prd_debian/wms_converter/convert_map.sh
curl -s http://localhost:8000/health && echo " API OK"
curl -s -X POST "http://localhost:8000/convert" -F "file=@/home/prd_debian/mapas/in/xml/04ed74c4f0144ec78ba5ce5e2cc97651_m_mapa_621622_0764_20251203125645.xml" | python3 -m json.tool | head -30
rm /home/prd_debian/mapas/in/json/*.json 2>/dev/null && echo "JSONs removidos para reprocessamento"
cd /home/prd_debian/wms_converter && source venv/bin/activate && python api.py &
sleep 2 && /home/prd_debian/wms_converter/convert_map.sh
curl -s http://localhost:8000/health
curl -s -X POST "http://localhost:8000/convert" -F "file=@/home/prd_debian/mapas/in/xml/0a4854c0cf174ef5bc88cd6fefb27978_m_mapa_622503_0764_20251215205433.xml" | python -m json.tool | head -50
/home/prd_debian/wms_converter/convert_map.sh
head -30 /home/prd_debian/mapas/in/json/input_622503.json
chmod +x /home/prd_debian/wms_converter/process_all.sh && /home/prd_debian/wms_converter/process_all.sh
cd /home/prd_debian/wms_converter && ./process_all.sh 2>&1 | head -100
ls -1 /home/prd_debian/mapas/in/json/*.json 2>/dev/null | wc -l
ls -1 /home/prd_debian/mapas/in/xml/*.xml 2>/dev/null | wc -l
tail -20 /home/prd_debian/mapas/in/json/input_622503.json
ls -lh /home/prd_debian/mapas/in/json/ | head -20
cat /home/prd_debian/mapas/in/json/input_621622.json | head -80
curl -x curl -X POST "http://localhost:8000/convert"   -F "file=@xml_620807_requisicao.xml"   -o ../mapas/in/input.json
sudo apt install culr
sudo apt install curl
clear
curl -x curl -X POST "http://localhost:8000/convert"   -F "file=@"   -o ../mapas/in/input.json
clear
curl -X POST "http://localhost:8000/convert"   -F "file=@/home/prd_debian/mapas/in/xml/xml_620807_requisicao.xml"   -o /tmp/temp.json
curl -X POST "http://localhost:8000/convert"   -F "file=@/home/prd_debian/mapas/in/xml/xml_620807_requisicao.xml"   -o \\wsl.localhost\Debian\home\prd_debian\mapas\in\json\input.json
clear
curl -X POST "http://localhost:8000/convert"   -F "file=@/home/prd_debian/mapas/in/xml/xml_620807_requisicao.xml"   -o \\wsl.localhost\Debian\home\prd_debian\mapas\in\json\input.json
curl -X POST "http://localhost:8000/convert"   -F "file=@/home/prd_debian/mapas/in/xml/xml_620807_requisicao.xml"   -o \\wsl.localhost\Debian\home\prd_debian\mapas;
clear
MAP=$(jq -r .Number /tmp/temp.json)
mv /tmp/temp.json /home/prd_debian/mapas/out/input_$MAP.json
echo "Salvo: input_$MAP.json"
/home/prd_debian/wms_converter/convert_map.sh
clear
/home/prd_debian/wms_converter/convert_map.sh
pkill -f "python api.py" && sleep 1 && cd /home/prd_debian/wms_converter && source venv/bin/activate && python api.py &
sleep 2 && curl -s -X POST "http://localhost:8000/convert" -F "file=@/home/prd_debian/mapas/in/xml/04ed74c4f0144ec78ba5ce5e2cc97651_m_mapa_621622_0764_20251203125645.xml" | python3 -m json.tool > /tmp/test_621622.json && head -80 /tmp/test_621622.json
curl -s http://localhost:8000/health
/home/prd_debian/wms_converter/convert_map.sh
head -100 /home/prd_debian/mapas/in/json/input_621622.json
rm /home/prd_debian/mapas/in/json/*.json 2>/dev/null; echo "JSONs antigos removidos"
cd /home/prd_debian/wms_converter && ./process_all.sh 2>&1 | tail -50
grep -A 5 "<pallet>" /home/prd_debian/mapas/in/xml/04ed74c4f0144ec78ba5ce5e2cc97651_m_mapa_621622_0764_20251203125645.xml | head -30
head -50 /home/prd_debian/mapas/in/xml/04ed74c4f0144ec78ba5ce5e2cc97651_m_mapa_621622_0764_20251203125645.xml
grep -l "ocpOrtec" /home/prd_debian/mapas/in/xml/*.xml | head -1
cat /home/prd_debian/mapas/in/xml/04ed74c4f0144ec78ba5ce5e2cc97651_m_mapa_621622_0764_20251203125645.xml | grep -i "baia\|pallet\|lado\|gaveta" | head -20
grep -r "não\|está\|código\|será\|após\|José" /home/prd_debian/wms_converter/*.py /home/prd_debian/wms_converter/modules/*.py 2>/dev/null | wc -l
python3 /home/prd_debian/wms_converter/convert.py --help 2>&1 | head -20
grep -n "→\|✓\|✗\|●\|○\|►\|▪" /home/prd_debian/wms_converter/*.py /home/prd_debian/wms_converter/modules/*.py 2>/dev/null
head -40 /home/prd_debian/wms_converter/convert.py
ls -la /home/prd_debian/wms_converter/ && echo "---" && ls -la /home/prd_debian/wms_converter/modules/
cd /home/prd_debian/wms_converter && curl -s http://localhost:8000/health && echo " - API OK"
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python test_config_generator.py
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python test_warehouse_config.py
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python test_config_generator.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main/data/route && rm -f 620768/config.json mapas_in/config.json && ls -la 620768/ mapas_in/
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python -m ocp_score-main.service.config_generator ocp_score-main/data/route/620768/input.json
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python -m ocp_score-main.service.config_generator ocp_score-main/data/route/mapas_in/input.json
cd /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768 && cat config_map_620815.json
cd /home/prd_debian/ocp_wms_core/ocp_score-main/data/route && rm -f 620768/config_map_620815.json mapas_in/config_map_620815.json
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python -m ocp_score-main.service.config_generator ocp_score-main/data/route/620768/input.json
cd /home/prd_debian/ocp_wms_core/ocp_score-main/database && head -20 Warehouse.csv | grep -E "UnbCode|916"
cd /home/prd_debian/ocp_wms_core/ocp_score-main/database && grep "916" Warehouse.csv | head -5
cd /home/prd_debian/ocp_wms_core/ocp_score-main/database && grep "^[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,764," Warehouse.csv
cd /home/prd_debian/ocp_wms_core/ocp_score-main/data/route && rm -f 620768/config_map_620815.json && cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python -m ocp_score-main.service.config_generator ocp_score-main/data/route/620768/input.json
cd /home/prd_debian/ocp_wms_core/ocp_score-main/data/route/620768 && cat config_map_620815.json | head -30
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && python -m ocp_score-main.service.config_generator ocp_score-main/data/route/mapas_in/input.json
cd /home/prd_debian/ocp_wms_core/ocp_score-main/data/route && ls -lh 620768/ mapas_in/
cd /home/prd_debian/ocp_wms_core && ls -la | grep -E "test_|\.json$"
cd /home/prd_debian/ocp_wms_core && rm -f test_config_generator.py test_config_output.json test_warehouse_config.py && echo "✓ Arquivos de teste removidos"
cd /home/prd_debian/ocp_wms_core && find . -maxdepth 2 -type f -name "*.log" -o -name "*batch*" -o -name "*temp*" 2>/dev/null | grep -v wms_venv
cd /home/prd_debian/ocp_wms_core && find ocp_score-main -type d -name "__pycache__" | head -10
cd /home/prd_debian/ocp_wms_core && find ocp_score-main -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; echo "✓ Cache Python removido"
cd /home/prd_debian/ocp_wms_core && ls -la | grep -v "^d" | grep -v "wms_venv"
ls
cd ..
code .
kill 124392 64294 2>/dev/null; sleep 1 && cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && python ocp_score-main/simple_api.py
curl -s http://localhost:5000/health && echo "" && curl -s http://localhost:8001/health
curl -s http://localhost:5000/health; echo ""
ps aux | grep -E "python.*api|python.*app.py" | grep -v grep
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && nohup python ocp_score-main/simple_api.py > /tmp/ocp_api.log 2>&1 &
sleep 2 && curl -s http://localhost:5000/health && echo "" && curl -s http://localhost:8001/health
curl -s http://localhost:8001/health/ && echo ""
curl -s http://localhost:8001/api/items-boxing/health/ && echo "" && echo "---" && curl -s http://localhost:8001/api/items-boxing/ | head -20
ps aux | grep -E "python.*(app\.py|simple_api)" | grep -v grep
cd /home/prd_debian/wms_converter && cat api.py | head -15
cd /home/prd_debian/wms_converter && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
cd /home/prd_debian/wms_converter && source venv/bin/activate && nohup python api.py > /tmp/wms_converter.log 2>&1 &
sleep 2 && curl -s http://localhost:8000/health && echo "" && curl -s http://localhost:8000/ | head -10
echo "=== APIs RODANDO ===" && ps aux | grep -E "python.*(api|app\.py)" | grep -v grep | awk '{print $2, $11, $12, $13}' && echo "" && echo "=== TESTES ===" && echo "1. wms-itemsboxing:" && curl -s http://localhost:8001/api/items-boxing/health/ && echo "" && echo "2. ocp_wms_core:" && curl -s http://localhost:5000/health | jq -c && echo "3. wms_converter:" && curl -s http://localhost:8000/ | jq -c
echo "=== TESTES DAS 3 APIs ===" && echo "" && echo "✅ API 1 - wms-itemsboxing (porta 8001):" && curl -s http://localhost:8001/api/items-boxing/health/ && echo "" && echo "" && echo "✅ API 2 - ocp_wms_core (porta 5000):" && curl -s http://localhost:5000/health && echo "" && echo "" && echo "✅ API 3 - wms_converter (porta 8000):" && curl -s http://localhost:8000/
tail -20 /tmp/wms_converter.log
curl -s http://localhost:8000/ && echo "" && curl -s http://localhost:8000/docs | head -5
cd /home/prd_debian && head -20 "data 2(Export).csv"
cd /home/prd_debian && wc -l "data 2(Export).csv"
cd /home/prd_debian && tail -20 "data 2(Export).csv"
cd /home/prd_debian && cut -d',' -f6 "data 2(Export).csv" | sort | uniq -c
cd /home/prd_debian && awk -F',' 'NR==1 || ($6=="MKTP" && NR<=30)' "data 2(Export).csv" | head -25
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python service/marketplace_detector.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python service/marketplace_detector.py 2>&1 | head -30
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python service/boxing_integrator.py 2>&1 | head -40
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && nohup python ocp_score-main/master_orchestrator.py > /tmp/orchestrator.log 2>&1 &
sleep 3 && curl -s http://localhost:9000/health && echo "" && echo "---" && curl -s http://localhost:9000/
tail -50 /tmp/orchestrator.log
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && nohup python ocp_score-main/master_orchestrator.py > /tmp/orchestrator.log 2>&1 &
sleep 3 && curl -s http://localhost:9000/health | python3 -m json.tool && echo "" && ps aux | grep master_orchestrator | grep -v grep
echo "=== STATUS DE TODAS AS APIs ===" && echo "" && echo "1. wms-itemsboxing (porta 8001):" && curl -s http://localhost:8001/api/items-boxing/health/ && echo "" && echo "" && echo "2. wms_converter (porta 8000):" && curl -s http://localhost:8000/health | python3 -m json.tool && echo "" && echo "3. ocp_wms_core (porta 5000):" && curl -s http://localhost:5000/health | python3 -m json.tool && echo "" && echo "4. Master Orchestrator (porta 9000):" && curl -s http://localhost:9000/ | python3 -m json.tool
echo "=== PROCESSANDO XML ATRAVÉS DO FLUXO COMPLETO ===" && echo "" && curl -X POST http://localhost:9000/process-xml-file -F "file=@/home/prd_debian/test_mapa_985625.xml" -F "format=json" 2>&1 | python3 -m json.tool
curl -X POST http://localhost:9000/process-xml-file -F "file=@/home/prd_debian/test_mapa_985625.xml" -F "format=json" -v 2>&1 | tail -100
pkill -f master_orchestrator.py && sleep 2
ls -la /home/prd_debian/ocp_wms_core/ocp_score-main/service/ | grep -E "pallet|calculator"
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && nohup python ocp_score-main/master_orchestrator.py > /tmp/orchestrator.log 2>&1 &
sleep 3 && curl -s http://localhost:9000/health | python3 -m json.tool
echo "=== PROCESSANDO MAPA 985625 ===" && echo "" && curl -X POST http://localhost:9000/process-xml-file -F "file=@/home/prd_debian/test_mapa_985625.xml" -F "format=json" 2>&1
echo "=== ANÁLISE DO PROCESSAMENTO ===" && echo "" && echo "📊 Resultado:" && cat /tmp/ocp_processing/20251222_160714/input.json | python3 -m json.tool | head -50
echo "" && echo "=== DETALHES DO PRODUTO ===" && cat /tmp/ocp_processing/20251222_160714/input.json | python3 -c "import json, sys; data=json.load(sys.stdin); print(f'Mapa: {data[\"Number\"]}'); print(f'Placa: {data[\"Vehicle\"][\"Plate\"]}'); print(f'Data Entrega: {data[\"DeliveryDate\"]}'); print(f'Total Pedidos: {len(data[\"Orders\"])}'); [print(f\"  Pedido {i+1}: {len(order[\"Items\"])} itens\") for i, order in enumerate(data[\"Orders\"])]"
echo "=== VERIFICANDO SKU 32683 ===" && grep "^32683," /home/prd_debian/data\ 2\(Export\).csv && echo "" && echo "Resultado: SKU 32683 NÃO é marketplace (não encontrado no CSV)" || echo "SKU 32683 não está na base marketplace"
echo "=== DETALHES DO ITEM ===" && cat /tmp/ocp_processing/20251222_160714/input.json | python3 -c "import json, sys; data=json.load(sys.stdin); item=data['Orders'][0]['Items'][0]; print(f'SKU: {item[\"Code\"]}'); print(f'Descrição: {item.get(\"Description\", \"N/A\")}'); print(f'Quantidade: {item[\"Quantity\"]} unidades'); print(f'Embalagem: {item.get(\"Packaging\", \"N/A\")}')"
echo "=== RESUMO DO PROCESSAMENTO COMPLETO ===" && echo "" && echo "✅ Fluxo executado:" && echo "  1. XML convertido para JSON ✓" && echo "  2. Config gerado automaticamente ✓" && echo "  3. Marketplace verificado: NÃO (SKU 32683 não é marketplace) ✓" && echo "  4. Boxing: PULADO (correto, não tem marketplace) ✓" && echo "  5. Paletização processada ✓" && echo "" && echo "📁 Arquivos gerados em: /tmp/ocp_processing/20251222_160714/" && ls -lh /tmp/ocp_processing/20251222_160714/ && echo "" && ls -lh /tmp/ocp_processing/20251222_160714/output/
echo "" && echo "=== CONFIG GERADO ===" && cat /tmp/ocp_processing/20251222_160714/config.json | python3 -m json.tool | head -30
echo "=== RELATÓRIO TXT GERADO ===" && cat /tmp/ocp_processing/20251222_160714/output/unknown-ocp-Rota.txt
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && python3 -c "
import sys
sys.path.insert(0, 'ocp_score-main')
import json
from service.config_generator import ConfigGenerator

# Lê os arquivos gerados
with open('/tmp/ocp_processing/20251222_160714/config.json') as f:
    config = json.load(f)
with open('/tmp/ocp_processing/20251222_160714/input.json') as f:
    input_data = json.load(f)

print('Config carregado:', list(config.keys()))
print('Input carregado:', list(input_data.keys()))
print('Mapa:', input_data['Number'])
print('Warehouse:', input_data['Warehouse']['UnbCode'])
"
echo "=== ARQUIVO TXT DE SAÍDA ===" && echo "" && cat /tmp/ocp_processing/20251222_160714/output/unknown-ocp-Rota.txt
echo "" && echo "=== LOCALIZAÇÃO DOS ARQUIVOS ===" && ls -lh /tmp/ocp_processing/20251222_160714/output/
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && bash GERAR_TXT_COMPLETO.sh
mkdir -p /home/prd_debian/mapas/in && cp /tmp/ocp_processing/20251222_160714/config.json /home/prd_debian/mapas/in/config_985625.json && cp /tmp/ocp_processing/20251222_160714/input.json /home/prd_debian/mapas/in/input_985625.json
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && curl -X POST 'http://localhost:5000/mapas/process/config_985625.json?data_file=input_985625.json&format=txt' -o /home/prd_debian/mapas/out/mapa_985625.txt 2>&1 | grep -v "%" && echo "" && ls -lh /home/prd_debian/mapas/out/mapa_985625.txt
echo "=== TXT GERADO DO MAPA 985625 ===" && cat /home/prd_debian/mapas/out/mapa_985625.txt
cp /tmp/ocp_processing/20251222_160714/config.json /home/prd_debian/mapas/in/config_completo.json && cp /tmp/ocp_processing/20251222_160714/input.json /home/prd_debian/mapas/in/inputcompleto.json && echo "Arquivos copiados para processamento"
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && bash GERAR_TXT_COMPLETO.sh 2>&1 | tail -30
cat /home/prd_debian/mapas/out/palletize_result_map_985625.txt
chmod +x /home/prd_debian/processar_xmls_massa.sh
cd /home/prd_debian && ls -lh processar_xmls_massa.sh
find /home/prd_debian/BinPacking/src/tests/samples/mapas_backtest -name "*.xml" | wc -l
mkdir -p /home/prd_debian/teste_massa && find /home/prd_debian/BinPacking/src/tests/samples/mapas_backtest -name "*.xml" | head -3 | xargs -I {} cp {} /home/prd_debian/teste_massa/ && ls -lh /home/prd_debian/teste_massa/
cd /home/prd_debian && ./processar_xmls_massa.sh /home/prd_debian/teste_massa 1
cat /home/prd_debian/mapas/out/processamento_massa/erro/m_mapa_965694_0575_20211005231813_error.log
cd /home/prd_debian && rm -rf /home/prd_debian/mapas/out/processamento_massa/* && ./processar_xmls_massa.sh /home/prd_debian/teste_massa 1 2>&1 | head -50
curl -s -X POST -F "file=@/home/prd_debian/teste_massa/m_mapa_965694_0575_20211005231813.xml" http://localhost:9000/process-xml-file | jq '.'
curl -s -X POST -F "file=@/home/prd_debian/teste_massa/m_mapa_965694_0575_20211005231813.xml" http://localhost:9000/process-xml-file | python3 -m json.tool 2>&1 | head -40
curl -s -X POST -F "file=@/home/prd_debian/teste_massa/m_mapa_965694_0575_20211005231813.xml" http://localhost:9000/process-xml-file 2>&1 | head -20
curl -s -X POST -F "file=@/home/prd_debian/teste_massa/m_mapa_965694_0575_20211005231813.xml" http://localhost:9000/process-xml-file > /tmp/response_test.txt && cat /tmp/response_test.txt
chmod +x /home/prd_debian/processar_massa_simples.sh && cd /home/prd_debian && rm -rf /home/prd_debian/mapas/out/processamento_massa/* && ./processar_massa_simples.sh /home/prd_debian/teste_massa
curl -s http://localhost:8000/health
curl -s -X POST -F "file=@/home/prd_debian/teste_massa/m_mapa_965634_0575_20211005231424.xml" http://localhost:8000/convert 2>&1 | head -30
cd /home/prd_debian && rm -rf /home/prd_debian/mapas/out/processamento_massa/* && timeout 60 ./processar_massa_simples.sh /home/prd_debian/teste_massa 2>&1
head -40 /home/prd_debian/mapas/out/processamento_massa/sucesso/m_mapa_965694_0575_20211005231813.txt
cat > /home/prd_debian/PROCESSAR_TODOS.sh << 'EOF'
#!/bin/bash
# Processar todos os 65 XMLs do diretório de testes

echo "🚀 Processando 65 XMLs..."
echo "⏱️  Tempo estimado: ~10-15 minutos"
echo ""

cd /home/prd_debian
./processar_massa_simples.sh /home/prd_debian/BinPacking/src/tests/samples/mapas_backtest

echo ""
echo "✅ Processamento concluído!"
echo "📁 Resultados em: /home/prd_debian/mapas/out/processamento_massa/"
EOF

chmod +x /home/prd_debian/PROCESSAR_TODOS.sh && echo "Script criado: PROCESSAR_TODOS.sh"
ls -lh /home/prd_debian/BinPacking/src/tests/samples/mapas_backtest/*.xml | head -10
mkdir -p /home/prd_debian/meus_xmls && ls -ld /home/prd_debian/meus_xmls
chmod +x /home/prd_debian/PROCESSAR_MEUS_XMLS.sh && echo "✅ Script criado!"
echo "📂 Estrutura de arquivos gerados:" && echo "" && echo "1️⃣ Arquivos intermediários (config + input):" && ls -lh /home/prd_debian/mapas/in/*.json 2>/dev/null | tail -5 && echo "" && echo "2️⃣ TXTs finais (sucessos):" && ls -lh /home/prd_debian/mapas/out/processamento_massa/sucesso/*.txt 2>/dev/null | tail -5 && echo "" && echo "3️⃣ XMLs com erro:" && ls -lh /home/prd_debian/mapas/out/processamento_massa/erro/*.xml 2>/dev/null | tail -5
cat << 'EOF'

📁 ONDE OS ARQUIVOS SÃO SALVOS:
═══════════════════════════════════════════════════════════════

🔄 Durante o processamento (temporários):
   /home/prd_debian/mapas/in/
   ├── config_completo.json  ← Config do database
   └── inputcompleto.json    ← Dados convertidos do XML

📊 Resultados finais:
   /home/prd_debian/mapas/out/processamento_massa/
   ├── sucesso/
   │   ├── m_mapa_XXXXXX.txt           ← TXT de paletização ✅
   │   └── m_mapa_XXXXXX_files/        ← JSONs intermediários
   │       ├── config.json
   │       ├── input.json
   │       └── marketplace_analysis.json
   ├── erro/
   │   └── m_mapa_XXXXXX.xml           ← XMLs que falharam ❌
   └── logs/
       └── processamento_YYYYMMDD_HHMMSS.log  ← Log detalhado

📄 TXTs individuais também ficam em:
   /home/prd_debian/mapas/out/
   └── palletize_result_map_XXXXXX.txt  ← TXT original

EOF

echo "📋 Exemplo real dos últimos arquivos gerados:" && echo "" && tree -L 2 /home/prd_debian/mapas/out/processamento_massa/ 2>/dev/null || find /home/prd_debian/mapas/out/processamento_massa/ -type f | head -10
clear
./ ./PROCESSAR_MEUS_XMLS.sh
./PROCESSAR_MEUS_XMLS.sh
CLEAR
clear
./PROCESSAR_MEUS_XMLS.sh
clear
./PROCESSAR_MEUS_XMLS.sh
cat /home/prd_debian/mapas/out/processamento_massa/logs/*.log 2>/dev/null | tail -50
grep -n "marketplace" /home/prd_debian/processar_massa_simples.sh
cd /home/prd_debian && rm -rf /home/prd_debian/mapas/out/processamento_massa/* && timeout 60 ./processar_massa_simples.sh /home/prd_debian/teste_massa 2>&1 | head -60
cat /home/prd_debian/mapas/out/processamento_massa/logs/resumo_boxing.csv
./PROCESSAR_MEUS_XMLS.sh
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH && python ocp_score-main/simple_api.py
lsof -i :5000
ss -tlnp | grep 5000
pkill -f "python app.py" && sleep 1 && cd /home/prd_debian/wms-itemsboxing/src && source ../venv/bin/activate && python app.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python api_server.py
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && export PYTHONPATH="/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH" && python ocp_score-main/api_server.py
cd /home/prd_debian/ocp_wms_core/ocp_score-main && source ../wms_venv/bin/activate && python api_server.py
cd /home/prd_debian/wms-itemsboxing/src && source ../venv/bin/activate && python app.py
cd /home/prd_debian/wms-itemsboxing/src && source ../venv/bin/activate && python app.py
cd /home/prd_debian && python3 --version && which python3
cd /home/prd_debian/wms-itemsboxing && ls -la run.sh && cat run.sh
cd /home/prd_debian/BinPacking && ls -la && pip3 install -e . 2>&1 | head -20
cd /home/prd_debian/wms-itemsboxing && python3 -m venv venv && source venv/bin/activate && cd src && pip install --upgrade pip && pip install -r requirements.txt
cd /home/prd_debian/wms-itemsboxing/src && source ../venv/bin/activate && cat requirements.txt | grep -v ddtrace > requirements_temp.txt && pip install -r requirements_temp.txt
cd /home/prd_debian/BinPacking/src && source /home/prd_debian/wms-itemsboxing/venv/bin/activate && pip install -e .
cd /home/prd_debian/wms-itemsboxing/src && source ../venv/bin/activate && pip install Flask==2.0.2 flask_restx==0.5.1 "numpy<2" pandas psutil py3dbp PyJWT==2.4.0 Werkzeug==2.0.2 parameterized sqlparse
cd /home/prd_debian/ocp_wms_core && source wms_venv/bin/activate && pip install -r ocp_score-main/requirements_api.txt
cd /home/prd_debian && ./PROCESSAR_MEUS_XMLS.sh
tail -50 /tmp/boxing.log
ls -lh /tmp/boxing.log && echo "---" && tail -30 /tmp/boxing.log 2>&1
curl -s http://localhost:8001/ 2>&1 | head -20
cd /home/prd_debian && timeout 30 ./PROCESSAR_MEUS_XMLS.sh 2>&1 | head -50
tail -50 /home/prd_debian/mapas/out/processamento_massa/logs/processamento_*.log | grep -A 2 "Debug:"
ls -lt /home/prd_debian/mapas/out/processamento_massa/logs/ | head -5
grep -A 1 "Debug:" /home/prd_debian/mapas/out/processamento_massa/logs/processamento_20251222_181007.log | head -20
chmod +x /home/prd_debian/apply_boxing.py && echo "✅ Script configurado"
cd /home/prd_debian && timeout 60 ./PROCESSAR_MEUS_XMLS.sh 2>&1 | head -60
ls -lt /home/prd_debian/mapas/out/processamento_massa/logs/ | head -3
DEBUG=1 python3 /home/prd_debian/apply_boxing.py /home/prd_debian/mapas/in/inputcompleto.json 2>&1 | head -30
source /home/prd_debian/wms_converter/venv/bin/activate && python /home/prd_debian/apply_boxing.py /home/prd_debian/mapas/in/inputcompleto.json 2>&1 | head -20
source /home/prd_debian/wms_converter/venv/bin/activate && python /home/prd_debian/apply_boxing.py /home/prd_debian/mapas/in/inputcompleto.json 2>&1
head -30 /home/prd_debian/mapas/in/inputcompleto.json
find /home/prd_debian/ocp_wms_core -name "GERAR_TXT*" -type f 2>/dev/null
source /home/prd_debian/wms_converter/venv/bin/activate && python /home/prd_debian/apply_boxing.py /home/prd_debian/mapas/in/inputcompleto.json 2>&1
cd /home/prd_debian && python3 << 'EOF'
import sys
sys.path.insert(0, '/home/prd_debian')
from apply_boxing import load_marketplace_skus
mktp = load_marketplace_skus()
print(f"Total SKUs marketplace: {len(mktp)}")
print(f"Exemplos: {list(mktp)[:10]}")
EOF

head -5 "/home/prd_debian/data 2(Export).csv" | cat -A
cd /home/prd_debian && python3 << 'EOF'
import sys
sys.path.insert(0, '/home/prd_debian')
from apply_boxing import load_marketplace_skus
mktp = load_marketplace_skus()
print(f"Total SKUs marketplace: {len(mktp)}")
print(f"Exemplos: {sorted(list(mktp))[:20]}")
EOF

cd /home/prd_debian && source /home/prd_debian/wms_converter/venv/bin/activate && timeout 30 bash -c '
# Processar um XML que tem marketplace
XML_FILE=$(ls /home/prd_debian/meus_xmls/*.xml | head -1)
echo "Processando: $(basename $XML_FILE)"

# Converter XML
curl -s -X POST -F "file=@$XML_FILE" http://localhost:8000/convert > /home/prd_debian/mapas/in/inputcompleto.json

# Verificar se tem marketplace
python3 << "PYEOF"
import json
with open("/home/prd_debian/mapas/in/inputcompleto.json") as f:
    data = json.load(f)
    
orders = data.get("Orders", [])
mktp_codes = ["1706", "1782", "10627", "22003", "22177", "1898"]
found = False

for order in orders:
    for item in order.get("Items", []):
        if str(item.get("Code")) in mktp_codes:
            print(f"✓ Encontrado MKTP SKU: {item.get(\"Code\")}")
            found = True
            
if not found:
    print("❌ Nenhum SKU marketplace neste XML")
PYEOF

# Aplicar boxing
echo "Aplicando boxing..."
python /home/prd_debian/apply_boxing.py /home/prd_debian/mapas/in/inputcompleto.json
'
cd /home/prd_debian && timeout 60 ./PROCESSAR_MEUS_XMLS.sh 2>&1 | head -80
tail -f /home/prd_debian/mapas/out/processamento_massa/logs/processamento_*.log 2>/dev/null | head -100
cd /home/prd_debian && ./validar_todos_mapas.sh /home/prd_debian/mapas_xml_saidas_filtrados /home/prd_debian/mapas/out/processamento_massa/sucesso 2>&1 | tee /tmp/validacao_final.log
clear
cat /home/prd_debian/mapas/out/relatorios_validacao/mapa_622225_validacao.txt
cat /home/prd_debian/mapas/out/relatorios_validacao/mapa_621902_validacao.txt
cat /home/prd_debian/mapas/out/relatorios_validacao/mapa_622187_validacao.txt
grep -n "622187" /home/prd_debian/mapas/out/processamento_massa/processamento_*.log 2>/dev/null | head -20
ls /home/prd_debian/mapas/out/processamento_massa/sucesso/*622187* 2>/dev/null | head -5
head -50 /home/prd_debian/mapas/out/processamento_massa/sucesso/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.txt | grep -i "box\|embalagem\|caixa"
grep "0141e22cdd024fb99e73e14a977d5554" /home/prd_debian/mapas/in/boxing_result.json 2>/dev/null || echo "Nenhum resultado de boxing encontrado"
grep -i "boxing\|marketplace" /home/prd_debian/mapas/out/processamento_massa/sucesso/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.txt | head -20
cat /home/prd_debian/meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml | grep -i "marketplace\|mktp" | head -5
cd /home/prd_debian && source wms_converter/venv/bin/activate && python3 apply_boxing.py /home/prd_debian/mapas/in/inputcompleto.json 2>&1 | head -20
cat /home/prd_debian/mapas/in/inputcompleto.json | python3 -m json.tool 2>/dev/null | head -50
cat /home/prd_debian/mapas/in/inputcompleto.json | python3 -c "import json, sys; data=json.load(sys.stdin); print('Orders:', len(data.get('Orders',[])));[print(f'  Client {o.get(\"Client\",{}).get(\"Code\")}: {len(o.get(\"Items\",[]))} items, First SKU: {o.get(\"Items\",[{}])[0].get(\"Code\") if o.get(\"Items\") else \"N/A\"}') for o in data.get('Orders',[])]"
grep "^2349," "/home/prd_debian/data 2(Export).csv"
for sku in 21530 21779 21791 21792; do echo -n "SKU $sku: "; grep "^$sku," "/home/prd_debian/data 2(Export).csv" | cut -d',' -f1,6 || echo "NÃO ENCONTRADO"; done
cd /home/prd_debian && python3 -c "
import json
with open('meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml', 'r') as f:
    content = f.read()
    print('Total SKU 21530:', content.count('Code>21530<'))
    print('Total SKU 21779:', content.count('Code>21779<'))
    print('Total SKU 21791:', content.count('Code>21791<'))
    print('Total SKU 21792:', content.count('Code>21792<'))
"
cd /home/prd_debian && python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('mapas_xml_saidas_filtrados/0141e22cdd024fb99e73e14a977d5554_ocp_622187_0764_20251210224010.xml')
root = tree.getroot()
for item in root.findall('.//Item'):
    code = item.find('Code')
    qty = item.find('Quantity')
    if code is not None and code.text in ['21530', '21779', '21791', '21792']:
        print(f'SKU {code.text}: {qty.text if qty is not None else 0} unidades')
"
find /home/prd_debian/mapas_xml_saidas* -name "*0141e22cdd024fb99e73e14a977d5554*" 2>/dev/null
grep -E "<Code>(21530|21779|21791|21792)</Code>" /home/prd_debian/mapas_xml_saidas_filtrados/0141e22cdd024fb99e73e14a977d5554_ocp_622187_0764_20251211013853.xml
python3 /home/prd_debian/comparar_xml_txt.py /home/prd_debian/mapas_xml_saidas_filtrados/0141e22cdd024fb99e73e14a977d5554_ocp_622187_0764_20251211013853.xml /home/prd_debian/mapas/out/processamento_massa/sucesso/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.txt 2>&1 | grep -A 25 "SKUs com Diferenças"
for sku in 21530 21779 21791 21792 22009 23651 24486 24488 27375 29197 29199 29201 29209 29215 32126 32354 32644 34410 34654; do echo -n "SKU $sku: "; grep "^$sku," "/home/prd_debian/data 2(Export).csv" | cut -d',' -f1,6 || echo "NÃO ENCONTRADO"; done
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('/home/prd_debian/meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml')
root = tree.getroot()

# Extrair todos os SKUs
skus = set()
for item in root.findall('.//Item'):
    code = item.find('Code')
    if code is not None and code.text:
        skus.add(code.text.strip())

print(f'Total SKUs únicos no XML entrada: {len(skus)}')
print('Primeiros 20 SKUs:', sorted(list(skus))[:20])
"
head -100 /home/prd_debian/meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml | grep -A 5 -B 5 "Code"
head -80 /home/prd_debian/meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml
cd /home/prd_debian/wms_converter && source venv/bin/activate && python3 -c "
from modules.converter import XmlConverter
converter = XmlConverter()
result = converter.convert('/home/prd_debian/meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml', None)
print(f'Total Orders: {len(result.get(\"Orders\", []))}')
for i, order in enumerate(result.get('Orders', [])[:5]):
    print(f'Order {i+1}: Client={order.get(\"Client\",{}).get(\"Code\")}, Items={len(order.get(\"Items\",[]))}')
    for j, item in enumerate(order.get('Items', [])[:10]):
        print(f'  Item {j+1}: SKU={item.get(\"Code\")}, Qty={item.get(\"Quantity\",{}).get(\"Sales\")}x{item.get(\"Quantity\",{}).get(\"Unit\")}')
"
cd /home/prd_debian && curl -s -X POST -F "file=@meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml" "http://localhost:8000/convert" > /tmp/test_convert.json && python3 -c "
import json
with open('/tmp/test_convert.json') as f:
    data = json.load(f)
    total_items = sum(len(order.get('Items', [])) for order in data.get('Orders', []))
    print(f'Total Orders: {len(data.get(\"Orders\", []))}')
    print(f'Total Items: {total_items}')
    
# Testar detector
import sys
sys.path.append('/home/prd_debian/ocp_wms_core/ocp_score-main')
from service.marketplace_detector import MarketplaceDetector
detector = MarketplaceDetector()
analysis = detector.analyze_input(data)
print(f'Marketplace items: {analysis[\"marketplace_count\"]}/{analysis[\"total_items\"]} ({analysis[\"marketplace_percentage\"]:.1f}%)')
print(f'Marketplace SKUs: {analysis[\"marketplace_skus\"][:10]}...')
"
cd /home/prd_debian && echo "Testando mapa 622187..." && source wms_converter/venv/bin/activate && curl -s -X POST -F "file=@meus_xmls/0141e22cdd024fb99e73e14a977d5554_m_mapa_622187_0764_20251210224010.xml" "http://localhost:8000/convert" > mapas/in/inputcompleto.json && python3 apply_boxing.py mapas/in/inputcompleto.json 2>&1 | head -10
clear
cd /home/prd_debian
./PROCESSAR_MEUS_XMLS.sh
cd /home/prd_debian && ./validar_todos_mapas.sh 2>&1 | tee /tmp/validacao_output.log
pkill -f validar_todos_mapas
sudo apt-get install -y bc 2>&1 | tail -5
ls /home/prd_debian/mapas_xml_saidas/*.xml | head -5
cd /home/prd_debian && ls mapas_xml_saidas/*.xml | head -20 | wc -l
cd /home/prd_debian && timeout 60 ./validar_todos_mapas.sh 2>&1 | head -100
cd /home/prd_debian && nohup ./validar_todos_mapas.sh > /tmp/validacao_completa.log 2>&1 &
echo $!
tail -30 /tmp/validacao_completa.log
ps aux | grep -E "validar_todos_mapas|444531" | grep -v grep
sleep 10 && tail -50 /tmp/validacao_completa.log | grep -E "\[|✅|Validação concluída"
ls -lh /home/prd_debian/mapas/out/relatorios_validacao/*.md | tail -1
head -100 /home/prd_debian/mapas/out/relatorios_validacao/validacao_consolidada_*.md | tail -50
kill 444531 444532 2>/dev/null; sleep 2; pkill -f validar_todos_mapas
cd /home/prd_debian && ls meus_xmls/*.xml | head -3 | xargs -I {} basename {} | cut -d'_' -f1
cd /home/prd_debian && ls meus_xmls/*.xml | wc -l
cd /home/prd_debian && for xml in meus_xmls/*.xml; do basename "$xml" | cut -d'_' -f1; done > /tmp/hashes_processados.txt && wc -l /tmp/hashes_processados.txt
cd /home/prd_debian/mapas_xml_saidas && for hash in $(cat /tmp/hashes_processados.txt); do ls ${hash}_*.xml 2>/dev/null; done | wc -l
mkdir -p /home/prd_debian/mapas_xml_saidas_filtrados && cd /home/prd_debian/mapas_xml_saidas && for hash in $(cat /tmp/hashes_processados.txt); do ls ${hash}_*.xml 2>/dev/null && cp ${hash}_*.xml /home/prd_debian/mapas_xml_saidas_filtrados/ 2>/dev/null; done | wc -l
ls /home/prd_debian/mapas_xml_saidas_filtrados/*.xml | wc -l
cd /home/prd_debian && ./PROCESSAR_MEUS_XMLS.sh
find /home/prd_debian/mapas/out -name "*622077*.txt" -type f 2>/dev/null | head -5
ls /home/prd_debian/mapas/out/processamento_massa/sucesso/ | grep 622077
cd /home/prd_debian && python3 << 'EOF'
import xml.etree.ElementTree as ET

# Parsear XML
xml_file = "/home/prd_debian/mapas_xml_saidas/05608282a5884f92aae29eee2b334a18_ocp_622077_0764_20251210013723.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

# Extrair dados do XML
xml_data = {}
total_pallets = 0
total_items_xml = 0

for pallet in root.findall('.//pallet'):
    total_pallets += 1
    lado = pallet.find('cdLado').text
    baia = pallet.find('nrBaiaGaveta').text
    pallet_id = f"P0{baia}_{lado}_{baia}"
    
    items = []
    for item in pallet.findall('.//item'):
        cd_item = item.find('cdItem').text
        qt_venda = int(item.find('qtUnVenda').text)
        qt_avulsa = int(item.find('qtUnAvulsa').text)
        total = qt_venda + qt_avulsa
        total_items_xml += total
        
        if cd_item not in [i[0] for i in items]:
            items.append([cd_item, total])
        else:
            for i in items:
                if i[0] == cd_item:
                    i[1] += total
    
    xml_data[pallet_id] = items

# Ler TXT e extrair dados
txt_file = "/home/prd_debian/mapas/out/processamento_massa/sucesso/05608282a5884f92aae29eee2b334a18_m_mapa_622077_0764_20251209223717.txt"
txt_data = {}
total_items_txt = 0

with open(txt_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    current_pallet = None
    
    for line in lines:
        # Identifica início de pallet
        if line.startswith('P0') and '_' in line:
            parts = line.split()
            current_pallet = parts[0]
            txt_data[current_pallet] = []
        
        # Identifica linhas com produtos (começam com | 0)
        elif current_pallet and '| 0' in line:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    codigo = parts[2]
                    # Procura quantidade (coluna após nome do produto)
                    for i in range(len(parts)):
                        if parts[i].isdigit() and int(parts[i]) > 0:
                            qtd = int(parts[i])
                            total_items_txt += qtd
                            txt_data[current_pallet].append([codigo, qtd])
                            break
                except:
                    pass

print(f"\n{'='*80}")
print(f"COMPARAÇÃO XML vs TXT - Mapa 622077")
print(f"{'='*80}\n")
print(f"📦 Total Pallets XML: {total_pallets}")
print(f"📦 Total Pallets TXT: {len(txt_data)}")
print(f"📊 Total Produtos XML: {total_items_xml}")
print(f"📊 Total Produtos TXT: {total_items_txt}")
print(f"\n{'='*80}")

# Comparar pallet a pallet
print(f"\n🔍 DIFERENÇAS POR PALLET:\n")
for pallet_id in sorted(xml_data.keys()):
    if pallet_id in txt_data:
        xml_items = {item[0]: item[1] for item in xml_data[pallet_id]}
        txt_items = {item[0]: item[1] for item in txt_data[pallet_id]}
        
        # Verifica diferenças
        all_codes = set(xml_items.keys()) | set(txt_items.keys())
        has_diff = False
        
        for code in all_codes:
            xml_qty = xml_items.get(code, 0)
            txt_qty = txt_items.get(code, 0)
            
            if xml_qty != txt_qty:
                if not has_diff:
                    print(f"\n{pallet_id}:")
                    has_diff = True
                status = "✅" if xml_qty == txt_qty else "❌"
                print(f"  {status} SKU {code}: XML={xml_qty}, TXT={txt_qty}, Diff={txt_qty-xml_qty}")
        
        if not has_diff:
            print(f"{pallet_id}: ✅ OK")
    else:
        print(f"{pallet_id}: ⚠️  NÃO ENCONTRADO NO TXT")

print(f"\n{'='*80}\n")
EOF

cd /home/prd_debian && python3 << 'EOF'
import xml.etree.ElementTree as ET
from collections import defaultdict

# Parsear XML
xml_file = "/home/prd_debian/mapas_xml_saidas/05608282a5884f92aae29eee2b334a18_ocp_622077_0764_20251210013723.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

print("\n" + "="*100)
print("📊 RELATÓRIO DE COMPARAÇÃO: XML SAÍDA vs TXT GERADO")
print("="*100)

# Extrair dados do XML
xml_pallets = {}
xml_total_items = 0
xml_skus_totals = defaultdict(int)

for pallet in root.findall('.//pallet'):
    lado = pallet.find('cdLado').text
    baia = pallet.find('nrBaiaGaveta').text
    pallet_key = f"P0{baia}_{lado}_0{baia}"
    
    items_dict = defaultdict(int)
    for item in pallet.findall('.//item'):
        cd_item = item.find('cdItem').text
        qt_venda = int(item.find('qtUnVenda').text)
        qt_avulsa = int(item.find('qtUnAvulsa').text)
        total = qt_venda + qt_avulsa
        
        items_dict[cd_item] += total
        xml_skus_totals[cd_item] += total
        xml_total_items += total
    
    xml_pallets[pallet_key] = dict(items_dict)

# Ler TXT
txt_file = "/home/prd_debian/mapas/out/processamento_massa/sucesso/05608282a5884f92aae29eee2b334a18_m_mapa_622077_0764_20251209223717.txt"
txt_pallets = {}
txt_total_items = 0
txt_skus_totals = defaultdict(int)

with open(txt_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    current_pallet = None
    
    for line in lines:
        if line.startswith('P0') and '_' in line:
            current_pallet = line.split()[0]
            txt_pallets[current_pallet] = defaultdict(int)
        
        elif current_pallet and '| 0' in line and '|=' not in line:
            parts = line.strip().split('|')
            if len(parts) >= 3:
                try:
                    data = parts[2].strip().split()
                    if len(data) >= 2:
                        codigo = data[0]
                        # Pega a quantidade (geralmente o último número antes do grupo/peso)
                        for d in reversed(data):
                            if d.isdigit() and int(d) > 0 and int(d) < 10000:
                                qtd = int(d)
                                txt_pallets[current_pallet][codigo] += qtd
                                txt_skus_totals[codigo] += qtd
                                txt_total_items += qtd
                                break
                except:
                    pass

# Converter defaultdict para dict
for key in txt_pallets:
    txt_pallets[key] = dict(txt_pallets[key])

print(f"\n📦 RESUMO GERAL:")
print(f"   XML: {len(xml_pallets)} pallets, {xml_total_items} unidades, {len(xml_skus_totals)} SKUs únicos")
print(f"   TXT: {len(txt_pallets)} pallets, {txt_total_items} unidades, {len(txt_skus_totals)} SKUs únicos")

# Comparação por pallet
print(f"\n🔍 COMPARAÇÃO PALLET POR PALLET:")
print("-" * 100)

pallets_ok = 0
pallets_diff = 0
skus_ok = 0
skus_diff = 0

for pallet_id in sorted(xml_pallets.keys()):
    xml_items = xml_pallets[pallet_id]
    txt_items = txt_pallets.get(pallet_id, {})
    
    all_skus = set(xml_items.keys()) | set(txt_items.keys())
    pallet_has_diff = False
    diff_details = []
    
    for sku in sorted(all_skus):
        xml_qty = xml_items.get(sku, 0)
        txt_qty = txt_items.get(sku, 0)
        
        if xml_qty == txt_qty:
            skus_ok += 1
        else:
            skus_diff += 1
            pallet_has_diff = True
            diff = txt_qty - xml_qty
            diff_details.append(f"      SKU {sku}: XML={xml_qty}, TXT={txt_qty} (diff: {diff:+d})")
    
    if pallet_has_diff:
        pallets_diff += 1
        print(f"\n❌ {pallet_id}: DIFERENÇAS ENCONTRADAS")
        print(f"   Total SKUs XML: {len(xml_items)}, Total SKUs TXT: {len(txt_items)}")
        for detail in diff_details[:10]:  # Mostra até 10 diferenças
            print(detail)
        if len(diff_details) > 10:
            print(f"      ... e mais {len(diff_details)-10} diferenças")
    else:
        pallets_ok += 1
        print(f"✅ {pallet_id}: OK ({len(xml_items)} SKUs, {sum(xml_items.values())} unidades)")

# Resumo final
print("\n" + "="*100)
print("📈 RESULTADO FINAL:")
print("-" * 100)
print(f"✅ Pallets Corretos: {pallets_ok}/{len(xml_pallets)}")
print(f"❌ Pallets com Diferenças: {pallets_diff}/{len(xml_pallets)}")
print(f"✅ SKUs Corretos: {skus_ok}")
print(f"❌ SKUs com Diferenças: {skus_diff}")

# Verifica SKUs faltando ou sobrando
all_skus = set(xml_skus_totals.keys()) | set(txt_skus_totals.keys())
missing_in_txt = []
missing_in_xml = []
qty_diffs = []

for sku in all_skus:
    xml_total = xml_skus_totals.get(sku, 0)
    txt_total = txt_skus_totals.get(sku, 0)
    
    if xml_total > 0 and txt_total == 0:
        missing_in_txt.append((sku, xml_total))
    elif txt_total > 0 and xml_total == 0:
        missing_in_xml.append((sku, txt_total))
    elif xml_total != txt_total:
        qty_diffs.append((sku, xml_total, txt_total, txt_total - xml_total))

if missing_in_txt:
    print(f"\n⚠️  SKUs no XML mas NÃO no TXT: {len(missing_in_txt)}")
    for sku, qty in missing_in_txt[:5]:
        print(f"   - SKU {sku}: {qty} unidades")

if missing_in_xml:
    print(f"\n⚠️  SKUs no TXT mas NÃO no XML: {len(missing_in_xml)}")
    for sku, qty in missing_in_xml[:5]:
        print(f"   - SKU {sku}: {qty} unidades")

if qty_diffs:
    print(f"\n⚠️  SKUs com QUANTIDADES DIFERENTES: {len(qty_diffs)}")
    for sku, xml_qty, txt_qty, diff in qty_diffs[:10]:
        print(f"   - SKU {sku}: XML={xml_qty}, TXT={txt_qty} (diff: {diff:+d})")

# Conclusão
print("\n" + "="*100)
if pallets_diff == 0 and skus_diff == 0:
    print("✅✅✅ PERFEITO! XML e TXT SÃO IDÊNTICOS! ✅✅✅")
else:
    accuracy = (skus_ok / (skus_ok + skus_diff) * 100) if (skus_ok + skus_diff) > 0 else 0
    print(f"⚠️  ATENÇÃO: Encontradas {skus_diff} diferenças ({accuracy:.1f}% de precisão)")
print("="*100 + "\n")
EOF

cd /home/prd_debian && python3 << 'EOF'
import xml.etree.ElementTree as ET
from collections import defaultdict
import re

# Parsear XML
xml_file = "/home/prd_debian/mapas_xml_saidas/05608282a5884f92aae29eee2b334a18_ocp_622077_0764_20251210013723.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

xml_pallets = {}
xml_total = 0
xml_skus = defaultdict(int)

for pallet in root.findall('.//pallet'):
    lado = pallet.find('cdLado').text
    baia = pallet.find('nrBaiaGaveta').text
    pallet_key = f"P0{baia}_{lado}_0{baia}"
    
    items_dict = defaultdict(int)
    for item in pallet.findall('.//item'):
        cd_item = item.find('cdItem').text
        qt_venda = int(item.find('qtUnVenda').text)
        qt_avulsa = int(item.find('qtUnAvulsa').text)
        total = qt_venda + qt_avulsa
        items_dict[cd_item] += total
        xml_skus[cd_item] += total
        xml_total += total
    
    xml_pallets[pallet_key] = dict(items_dict)

# Ler TXT com regex melhorado
txt_file = "/home/prd_debian/mapas/out/processamento_massa/sucesso/05608282a5884f92aae29eee2b334a18_m_mapa_622077_0764_20251209223717.txt"
txt_pallets = {}
txt_total = 0
txt_skus = defaultdict(int)

with open(txt_file, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    current_pallet = None
    
    for line in lines:
        # Detecta início de pallet: P01_A_01, P02_M_02, etc
        pallet_match = re.match(r'^(P\d{2}_[AM]_\d{2})_', line)
        if pallet_match:
            current_pallet = pallet_match.group(1)
            txt_pallets[current_pallet] = defaultdict(int)
        
        # Detecta linhas de produto: | 0 <spaces> CODIGO <nome> <qtd> <resto>
        elif current_pallet and line.strip().startswith('| 0'):
            # Remove pipes e split
            cleaned = line.replace('|', ' ').strip()
            parts = cleaned.split()
            
            # Formato: 0 CODIGO NOME... QTD EMBALAGEM GRUPO PESO ATRIBUTO OCUPACAO
            if len(parts) >= 3:
                try:
                    sku = parts[1]  # Segundo campo após o 0
                    # Procura a quantidade (número antes da embalagem/grupo)
                    # Geralmente está após a descrição
                    for i in range(2, len(parts)):
                        if parts[i].isdigit():
                            qtd = int(parts[i])
                            if qtd > 0 and qtd < 100000:  # Filtro razoável
                                txt_pallets[current_pallet][sku] += qtd
                                txt_skus[sku] += qtd
                                txt_total += qtd
                                break
                except (ValueError, IndexError):
                    pass

# Converte defaultdict para dict
for key in txt_pallets:
    txt_pallets[key] = dict(txt_pallets[key])

print("\n" + "="*100)
print("📊 RELATÓRIO DETALHADO: XML vs TXT - Mapa 622077")
print("="*100)

print(f"\n📦 TOTAIS:")
print(f"   XML: {len(xml_pallets)} pallets | {xml_total} unidades | {len(xml_skus)} SKUs")
print(f"   TXT: {len(txt_pallets)} pallets | {txt_total} unidades | {len(txt_skus)} SKUs")
print(f"   Diferença: {txt_total - xml_total:+d} unidades")

# Comparação pallet por pallet
print(f"\n🔍 COMPARAÇÃO POR PALLET:")
print("-" * 100)

match_pallets = 0
total_sku_matches = 0
total_sku_diffs = 0

for pallet_id in sorted(xml_pallets.keys()):
    xml_items = xml_pallets[pallet_id]
    txt_items = txt_pallets.get(pallet_id, {})
    
    xml_sum = sum(xml_items.values())
    txt_sum = sum(txt_items.values())
    
    # Conta matches de SKUs
    all_skus = set(xml_items.keys()) | set(txt_items.keys())
    matches = sum(1 for sku in all_skus if xml_items.get(sku, 0) == txt_items.get(sku, 0))
    diffs = len(all_skus) - matches
    
    total_sku_matches += matches
    total_sku_diffs += diffs
    
    status = "✅" if xml_sum == txt_sum and diffs == 0 else "❌"
    
    if diffs == 0:
        match_pallets += 1
        print(f"{status} {pallet_id:12} | SKUs: {len(xml_items):2} | Un: {xml_sum:4} → {txt_sum:4} | OK")
    else:
        print(f"{status} {pallet_id:12} | SKUs: {len(xml_items):2} → {len(txt_items):2} | Un: {xml_sum:4} → {txt_sum:4} | Diff: {diffs}")

# Análise de SKUs com diferenças
print(f"\n📝 DETALHES DAS DIFERENÇAS:")
print("-" * 100)

all_skus = set(xml_skus.keys()) | set(txt_skus.keys())
diffs_detail = []

for sku in sorted(all_skus):
    xml_qty = xml_skus.get(sku, 0)
    txt_qty = txt_skus.get(sku, 0)
    
    if xml_qty != txt_qty:
        diff = txt_qty - xml_qty
        diffs_detail.append((sku, xml_qty, txt_qty, diff))

if diffs_detail:
    print(f"\nTotal de SKUs com diferenças: {len(diffs_detail)}")
    print("\nPrimeiros 20:")
    for sku, xml_qty, txt_qty, diff in diffs_detail[:20]:
        status = "❌ Falta" if diff < 0 else "⚠️  Sobra"
        print(f"  {status} SKU {sku:6} | XML: {xml_qty:4} | TXT: {txt_qty:4} | Diff: {diff:+5}")

# Resultado final
print("\n" + "="*100)
print("📈 RESULTADO:")
accuracy = (total_sku_matches / (total_sku_matches + total_sku_diffs) * 100) if (total_sku_matches + total_sku_diffs) > 0 else 0
print(f"   Pallets OK: {match_pallets}/{len(xml_pallets)} ({match_pallets/len(xml_pallets)*100:.1f}%)")
print(f"   SKUs OK: {total_sku_matches}/{total_sku_matches + total_sku_diffs} ({accuracy:.1f}%)")
print(f"   Unidades: {xml_total} → {txt_total} ({txt_total - xml_total:+d})")

if match_pallets == len(xml_pallets) and total_sku_diffs == 0:
    print("\n✅✅✅ PERFEITO! RESULTADOS IDÊNTICOS! ✅✅✅")
else:
    print(f"\n⚠️  ATENÇÃO: {total_sku_diffs} SKUs com diferenças")
print("="*100 + "\n")
EOF

grep -A 3 "P01_A_01" /home/prd_debian/mapas/out/processamento_massa/sucesso/05608282a5884f92aae29eee2b334a18_m_mapa_622077_0764_20251209223717.txt | head -10
cd /home/prd_debian && python3 << 'EOF'
import xml.etree.ElementTree as ET
from collections import defaultdict
import re

# Parsear XML
xml_file = "/home/prd_debian/mapas_xml_saidas/05608282a5884f92aae29eee2b334a18_ocp_622077_0764_20251210013723.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

xml_pallets = {}
xml_total = 0
xml_skus = defaultdict(int)

for pallet in root.findall('.//pallet'):
    lado = pallet.find('cdLado').text
    baia = pallet.find('nrBaiaGaveta').text
    pallet_key = f"P0{baia}_{lado}_0{baia}"
    
    items_dict = defaultdict(int)
    for item in pallet.findall('.//item'):
        cd_item = item.find('cdItem').text
        qt_venda = int(item.find('qtUnVenda').text)
        qt_avulsa = int(item.find('qtUnAvulsa').text)
        total = qt_venda + qt_avulsa
        items_dict[cd_item] += total
        xml_skus[cd_item] += total
        xml_total += total
    
    xml_pallets[pallet_key] = dict(items_dict)

# Ler TXT linha por linha considerando formato correto
txt_file = "/home/prd_debian/mapas/out/processamento_massa/sucesso/05608282a5884f92aae29eee2b334a18_m_mapa_622077_0764_20251209223717.txt"
txt_pallets = {}
txt_total = 0
txt_skus = defaultdict(int)

with open(txt_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    current_pallet = None
    
    for line in lines:
        # Detecta pallet: P01_A_01_1/35 ...
        if re.match(r'^P\d{2}_[AM]_\d{2}_', line):
            match = re.match(r'^(P\d{2}_[AM]_\d{2})_', line)
            if match:
                current_pallet = match.group(1)
                txt_pallets[current_pallet] = defaultdict(int)
        
        # Linha de produto: | 0       SKU         DESCRICAO...                  QTD EMBALAGEM...
        elif current_pallet and line.strip().startswith('| 0'):
            try:
                # Remove pipes e espaços extras
                cleaned = line.replace('|', '').strip()
                
                # Regex para capturar: 0 <SKU> <DESCRIÇÃO> <QTD> <EMBALAGEM>
                # Formato: "0       18856         MULTPACK... C/15                   200 4002 40/4002"
                match = re.search(r'0\s+(\d+)\s+.*?\s+(\d+)\s+\d{4}\s+\d+/\d+', cleaned)
                
                if match:
                    sku = match.group(1)
                    qtd = int(match.group(2))
                    
                    txt_pallets[current_pallet][sku] += qtd
                    txt_skus[sku] += qtd
                    txt_total += qtd
            except Exception as e:
                pass

# Converter defaultdict para dict
for key in txt_pallets:
    txt_pallets[key] = dict(txt_pallets[key])

print("\n" + "="*100)
print("📊 RELATÓRIO DE VALIDAÇÃO: XML ORTEC vs TXT GERADO")
print("="*100)
print(f"\nMapa: 622077")
print(f"Data: 2025-12-10")

print(f"\n📦 RESUMO QUANTITATIVO:")
print(f"{'':20} {'XML':>10} {'TXT':>10} {'Diferença':>15}")
print("-" * 100)
print(f"{'Pallets':20} {len(xml_pallets):>10} {len(txt_pallets):>10} {len(txt_pallets)-len(xml_pallets):>15}")
print(f"{'Unidades Total':20} {xml_total:>10} {txt_total:>10} {txt_total-xml_total:>+15}")
print(f"{'SKUs Únicos':20} {len(xml_skus):>10} {len(txt_skus):>10} {len(txt_skus)-len(xml_skus):>+15}")

# Comparação pallet por pallet
print(f"\n🔍 ANÁLISE POR PALLET:")
print("-" * 100)
print(f"{'Pallet':15} {'XML SKUs':>10} {'TXT SKUs':>10} {'XML Qtd':>10} {'TXT Qtd':>10} {'Status':>15}")
print("-" * 100)

match_pallets = 0
total_sku_matches = 0
total_skus_checked = 0

for pallet_id in sorted(xml_pallets.keys()):
    xml_items = xml_pallets[pallet_id]
    txt_items = txt_pallets.get(pallet_id, {})
    
    xml_sum = sum(xml_items.values())
    txt_sum = sum(txt_items.values())
    
    # Conta matches de SKUs
    all_skus = set(xml_items.keys()) | set(txt_items.keys())
    matches = sum(1 for sku in all_skus if xml_items.get(sku, 0) == txt_items.get(sku, 0))
    
    total_sku_matches += matches
    total_skus_checked += len(all_skus)
    
    status = "✅ MATCH" if xml_sum == txt_sum and matches == len(all_skus) else "❌ DIFF"
    if status == "✅ MATCH":
        match_pallets += 1
    
    print(f"{pallet_id:15} {len(xml_items):>10} {len(txt_items):>10} {xml_sum:>10} {txt_sum:>10} {status:>15}")

# Análise detalhada de diferenças
print(f"\n📝 DIFERENÇAS ENCONTRADAS:")
print("-" * 100)

all_skus = set(xml_skus.keys()) | set(txt_skus.keys())
exact_matches = []
diffs = []

for sku in sorted(all_skus):
    xml_qty = xml_skus.get(sku, 0)
    txt_qty = txt_skus.get(sku, 0)
    
    if xml_qty == txt_qty:
        exact_matches.append(sku)
    else:
        diffs.append((sku, xml_qty, txt_qty, txt_qty - xml_qty))

if diffs:
    print(f"\nSKUs com diferenças ({len(diffs)}):")
    print(f"{'SKU':>8} {'XML Qtd':>10} {'TXT Qtd':>10} {'Diferença':>12} {'Status':>15}")
    print("-" * 100)
    for sku, xml_qty, txt_qty, diff in diffs[:30]:
        if xml_qty == 0:
            status = "⚠️  Só no TXT"
        elif txt_qty == 0:
            status = "⚠️  Só no XML"
        else:
            status = "❌ Divergente"
        print(f"{sku:>8} {xml_qty:>10} {txt_qty:>10} {diff:>+12} {status:>15}")
    
    if len(diffs) > 30:
        print(f"\n... e mais {len(diffs)-30} diferenças")

# Resultado final
print("\n" + "="*100)
print("📈 RESULTADO FINAL DA VALIDAÇÃO:")
print("-" * 100)

pallet_accuracy = (match_pallets / len(xml_pallets) * 100) if xml_pallets else 0
sku_accuracy = (total_sku_matches / total_skus_checked * 100) if total_skus_checked else 0
unit_diff_pct = ((txt_total - xml_total) / xml_total * 100) if xml_total else 0

print(f"✓ Pallets Corretos: {match_pallets}/{len(xml_pallets)} ({pallet_accuracy:.1f}%)")
print(f"✓ SKUs Corretos: {total_sku_matches}/{total_skus_checked} ({sku_accuracy:.1f}%)")
print(f"✓ SKUs Idênticos: {len(exact_matches)}/{len(all_skus)}")
print(f"✗ SKUs Diferentes: {len(diffs)}/{len(all_skus)}")
print(f"⚠  Diferença de Unidades: {txt_total - xml_total:+d} ({unit_diff_pct:+.2f}%)")

print("\n" + "="*100)
if match_pallets == len(xml_pallets) and len(diffs) == 0:
    print("��🎉🎉 PERFEITO! XML E TXT SÃO 100% IDÊNTICOS! 🎉🎉🎉")
elif pallet_accuracy >= 80 and sku_accuracy >= 90:
    print(f"✅ BOM! Precisão de {sku_accuracy:.1f}% - Pequenas divergências")
else:
    print(f"⚠️  ATENÇÃO! Precisão de {sku_accuracy:.1f}% - Verificar divergências")
print("="*100 + "\n")
EOF

grep -A 10 "fora do caminhão" /home/prd_debian/mapas/out/processamento_massa/sucesso/05608282a5884f92aae29eee2b334a18_m_mapa_622077_0764_20251209223717.txt
chmod +x /home/prd_debian/comparar_xml_txt.py && python3 /home/prd_debian/comparar_xml_txt.py /home/prd_debian/mapas_xml_saidas/05608282a5884f92aae29eee2b334a18_ocp_622077_0764_20251210013723.xml /home/prd_debian/mapas/out/processamento_massa/sucesso/05608282a5884f92aae29eee2b334a18_m_mapa_622077_0764_20251209223717.txt
chmod +x /home/prd_debian/validar_todos_mapas.sh && echo "✅ Script criado e pronto para uso!"
clear
cd /home/prd_debian && ./validar_todos_mapas.sh 2>&1 | tail -100
cd /home/prd_debian && ./validar_todos_mapas.sh 2>&1 | tail -150
cd /home/prd_debian && ./validar_todos_mapas.sh 2>&1 | head -80
cat > /home/prd_debian/validar_todos_mapas.sh << 'SCRIPTEOF'
#!/bin/bash

# Script de validação em massa: XML ORTEC vs TXT gerado
# Compara todos os XMLs ORTEC com os TXTs gerados

PASTA_XML="${1:-/home/prd_debian/mapas_xml_saidas}"
PASTA_TXT="${2:-/home/prd_debian/mapas/out/processamento_massa/sucesso}"
RELATORIO_DIR="/home/prd_debian/mapas/out/relatorios_validacao"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RELATORIO_CONSOLIDADO="$RELATORIO_DIR/validacao_consolidada_$TIMESTAMP.md"

# Criar diretório de relatórios
mkdir -p "$RELATORIO_DIR"

# Contadores
TOTAL_XMLS=0
PROCESSADOS=0
SUCESSOS=0
FALHAS=0
NAO_ENCONTRADOS=0

# Arrays para rastreamento
declare -a MAPAS_OK
declare -a MAPAS_DIFF
declare -a MAPAS_NAO_ENCONTRADOS

# Banner
clear
cat << EOF
╔═══════════════════════════════════════════════════════════════╗
║     VALIDAÇÃO EM MASSA: XML ORTEC vs TXT GERADO              ║
╚═══════════════════════════════════════════════════════════════╝

📁 Pasta XMLs: $PASTA_XML
📁 Pasta TXTs: $PASTA_TXT
📄 Relatório: $RELATORIO_CONSOLIDADO

EOF

# Contar XMLs
TOTAL_XMLS=$(find "$PASTA_XML" -name "*.xml" | wc -l)
echo "📊 Total de XMLs encontrados: $TOTAL_XMLS"
echo ""
echo "🚀 Iniciando validação..."
echo ""

# Iniciar relatório consolidado em Markdown
cat > "$RELATORIO_CONSOLIDADO" << 'EOF'
# 📊 RELATÓRIO DE VALIDAÇÃO - XML ORTEC vs TXT GERADO

EOF

echo "**Data:** $(date '+%Y-%m-%d %H:%M:%S')  " >> "$RELATORIO_CONSOLIDADO"
echo "**Pasta XMLs:** \`$PASTA_XML\`  " >> "$RELATORIO_CONSOLIDADO"
echo "**Pasta TXTs:** \`$PASTA_TXT\`  " >> "$RELATORIO_CONSOLIDADO"
echo "**Total XMLs:** $TOTAL_XMLS" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "---" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "## 📋 Resultados por Mapa" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"

# Processar cada XML
for XML_FILE in "$PASTA_XML"/*.xml; do
    [ ! -f "$XML_FILE" ] && continue
    
    BASENAME=$(basename "$XML_FILE")
    HASH=$(echo "$BASENAME" | cut -d'_' -f1)
    MAPA_NUM=$(echo "$BASENAME" | grep -oP 'mapa_\K\d+' || echo "UNKNOWN")
    
    # Encontrar TXT correspondente
    TXT_FILE=$(find "$PASTA_TXT" -name "${HASH}_*.txt" | head -1)
    
    if [ ! -f "$TXT_FILE" ]; then
        NAO_ENCONTRADOS=$((NAO_ENCONTRADOS + 1))
        MAPAS_NAO_ENCONTRADOS+=("$MAPA_NUM")
        
        echo "" >> "$RELATORIO_CONSOLIDADO"
        echo "### ❌ Mapa $MAPA_NUM - TXT NÃO ENCONTRADO" >> "$RELATORIO_CONSOLIDADO"
        echo "" >> "$RELATORIO_CONSOLIDADO"
        echo "- **XML:** \`$BASENAME\`" >> "$RELATORIO_CONSOLIDADO"
        echo "- **Status:** TXT correspondente não encontrado" >> "$RELATORIO_CONSOLIDADO"
        echo "" >> "$RELATORIO_CONSOLIDADO"
        continue
    fi
    
    PROCESSADOS=$((PROCESSADOS + 1))
    
    echo "[$PROCESSADOS/$TOTAL_XMLS] Validando Mapa $MAPA_NUM..."
    
    # Executar comparação
    TEMP_RESULT="/tmp/comparacao_$MAPA_NUM.txt"
    python3 /home/prd_debian/comparar_xml_txt.py "$XML_FILE" "$TXT_FILE" > "$TEMP_RESULT" 2>&1
    
    # Extrair métricas do resultado
    SKU_ACC=$(grep "SKUs Idênticos:" "$TEMP_RESULT" | grep -oP '\d+\.\d+%' || echo "0.0%")
    DIFF_UN=$(grep "Diferença de Unidades:" "$TEMP_RESULT" | grep -oP '[+-]\d+' || echo "0")
    DIFF_PCT=$(grep "Diferença de Unidades:" "$TEMP_RESULT" | grep -oP '[+-]\d+\.\d+%' | tail -1 || echo "0.0%")
    TOTAL_XML=$(grep "Unidades Total" "$TEMP_RESULT" | awk '{print $3}' | head -1 || echo "0")
    TOTAL_TXT=$(grep "Unidades Total" "$TEMP_RESULT" | awk '{print $4}' | head -1 || echo "0")
    
    # Extrair SKUs com problemas
    SKUS_PROBLEMA=$(grep -A 20 "SKUs com Diferenças:" "$TEMP_RESULT" | grep "⚠️\|❌" | head -5 || echo "")
    
    # Verificar se é sucesso (>= 80% de precisão)
    SKU_NUM=$(echo "$SKU_ACC" | sed 's/%//')
    
    if (( $(echo "$SKU_NUM >= 80" | bc -l) )); then
        SUCESSOS=$((SUCESSOS + 1))
        MAPAS_OK+=("$MAPA_NUM:$SKU_ACC")
        STATUS="✅"
        STATUS_TEXT="APROVADO"
    else
        FALHAS=$((FALHAS + 1))
        MAPAS_DIFF+=("$MAPA_NUM:$SKU_ACC")
        STATUS="❌"
        STATUS_TEXT="DIVERGENTE"
    fi
    
    # Adicionar ao relatório consolidado com mais detalhes
    echo "" >> "$RELATORIO_CONSOLIDADO"
    echo "### $STATUS Mapa $MAPA_NUM - $STATUS_TEXT" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    echo "| Métrica | Valor |" >> "$RELATORIO_CONSOLIDADO"
    echo "|---------|-------|" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Precisão SKUs** | $SKU_ACC |" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Unidades XML** | $TOTAL_XML |" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Unidades TXT** | $TOTAL_TXT |" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Diferença** | $DIFF_UN ($DIFF_PCT) |" >> "$RELATORIO_CONSOLIDADO"
    
    if [ "$STATUS" = "❌" ] && [ -n "$SKUS_PROBLEMA" ]; then
        echo "" >> "$RELATORIO_CONSOLIDADO"
        echo "**🔍 Diagnóstico - Principais Divergências:**" >> "$RELATORIO_CONSOLIDADO"
        echo "\`\`\`" >> "$RELATORIO_CONSOLIDADO"
        echo "$SKUS_PROBLEMA" >> "$RELATORIO_CONSOLIDADO"
        echo "\`\`\`" >> "$RELATORIO_CONSOLIDADO"
    fi
    echo "" >> "$RELATORIO_CONSOLIDADO"
    
    # Salvar relatório individual
    RELATORIO_IND="$RELATORIO_DIR/mapa_${MAPA_NUM}_validacao.txt"
    cp "$TEMP_RESULT" "$RELATORIO_IND"
    rm -f "$TEMP_RESULT"
done

# Adicionar resumo ao relatório consolidado
if [ $PROCESSADOS -gt 0 ]; then
    if [ $SUCESSOS -gt 0 ]; then
        PERC_SUCESSO=$(echo "scale=1; $SUCESSOS * 100 / $PROCESSADOS" | bc)
    else
        PERC_SUCESSO="0.0"
    fi
    PERC_FALHAS=$(echo "scale=1; $FALHAS * 100 / $PROCESSADOS" | bc)
    PERC_NAO_ENC=$(echo "scale=1; $NAO_ENCONTRADOS * 100 / $TOTAL_XMLS" | bc)
else
    PERC_SUCESSO="0.0"
    PERC_FALHAS="0.0"
    PERC_NAO_ENC="0.0"
fi

cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## 📈 RESUMO GERAL

EOF

echo "| Métrica | Quantidade | Percentual |" >> "$RELATORIO_CONSOLIDADO"
echo "|---------|------------|------------|" >> "$RELATORIO_CONSOLIDADO"
echo "| **Total Processados** | $PROCESSADOS | 100% |" >> "$RELATORIO_CONSOLIDADO"
echo "| ✅ **Aprovados (≥80%)** | $SUCESSOS | ${PERC_SUCESSO}% |" >> "$RELATORIO_CONSOLIDADO"
echo "| ❌ **Com Divergências** | $FALHAS | ${PERC_FALHAS}% |" >> "$RELATORIO_CONSOLIDADO"
echo "| ⚠️  **TXT Não Encontrado** | $NAO_ENCONTRADOS | ${PERC_NAO_ENC}% |" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "### 🎯 Taxa de Aprovação: **${PERC_SUCESSO}%**" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "---" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"

# Listar mapas OK
if [ ${#MAPAS_OK[@]} -gt 0 ]; then
    cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'
## ✅ MAPAS APROVADOS (Precisão ≥80%)

EOF
    echo "Total: ${#MAPAS_OK[@]} mapas" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    for mapa in "${MAPAS_OK[@]}"; do
        MAPA_NUM=$(echo "$mapa" | cut -d':' -f1)
        PRECISAO=$(echo "$mapa" | cut -d':' -f2)
        echo "- **Mapa $MAPA_NUM**: $PRECISAO" >> "$RELATORIO_CONSOLIDADO"
    done
    echo "" >> "$RELATORIO_CONSOLIDADO"
fi

# Listar mapas com divergências
if [ ${#MAPAS_DIFF[@]} -gt 0 ]; then
    cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## ❌ MAPAS COM DIVERGÊNCIAS (Precisão menor que 80%)

EOF
    echo "Total: ${#MAPAS_DIFF[@]} mapas" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    echo "**⚠️  Estes mapas requerem atenção e revisão!**" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    for mapa in "${MAPAS_DIFF[@]}"; do
        MAPA_NUM=$(echo "$mapa" | cut -d':' -f1)
        PRECISAO=$(echo "$mapa" | cut -d':' -f2)
        echo "- **Mapa $MAPA_NUM**: $PRECISAO ⚠️" >> "$RELATORIO_CONSOLIDADO"
    done
    echo "" >> "$RELATORIO_CONSOLIDADO"
fi

# Listar mapas não encontrados
if [ ${#MAPAS_NAO_ENCONTRADOS[@]} -gt 0 ]; then
    cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## ⚠️  MAPAS SEM TXT CORRESPONDENTE

EOF
    echo "Total: ${#MAPAS_NAO_ENCONTRADOS[@]} mapas" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    for mapa in "${MAPAS_NAO_ENCONTRADOS[@]}"; do
        echo "- Mapa $mapa" >> "$RELATORIO_CONSOLIDADO"
    done
    echo "" >> "$RELATORIO_CONSOLIDADO"
fi

cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## 📂 Arquivos Gerados

EOF
echo "- **Relatório consolidado**: \`$RELATORIO_CONSOLIDADO\`" >> "$RELATORIO_CONSOLIDADO"
echo "- **Relatórios individuais**: \`$RELATORIO_DIR/mapa_*_validacao.txt\`" >> "$RELATORIO_CONSOLIDADO"

cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## 🔍 Diagnóstico Geral

### Tipos de Divergências Comuns:

1. **SKUs Faltando no TXT** - Produtos que aparecem no XML mas não no TXT gerado
   - Geralmente são produtos TopoPallet (chicletes, balas, pequenos itens)
   
2. **Diferenças de Quantidade** - Quantidades divergentes entre XML e TXT
   - Podem indicar problemas no processamento ou arredondamento

3. **Produtos Fora do Caminhão** - Itens que não couberam na paletização
   - Verificar se estão corretamente identificados na seção "fora do caminhão"

### Recomendações:

- ✅ Mapas com **≥95%** de precisão: Excelente, sem ação necessária
- ⚠️  Mapas com **80-94%** de precisão: Revisar diferenças específicas
- ❌ Mapas com **menos de 80%** de precisão: Investigar causa raiz e reprocessar

---

EOF
echo "**Gerado em:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$RELATORIO_CONSOLIDADO"

echo ""
echo "📄 Relatório consolidado: $RELATORIO_CONSOLIDADO"
echo "📂 Relatórios individuais: $RELATORIO_DIR/mapa_*_validacao.txt"
echo ""
echo "✅ Validação concluída!"
SCRIPTEOF

chmod +x /home/prd_debian/validar_todos_mapas.sh && echo "✅ Script recriado!"
ps aux | grep -E "processar_massa|PROCESSAR" | grep -v grep
ls -lht /home/prd_debian/mapas/out/processamento_massa/logs/ | head -3
tail -30 /home/prd_debian/mapas/out/processamento_massa/logs/processamento_20251222_182045.log
find /home/prd_debian/ocp_wms_core -name "*config*" -type f | grep -E "\.json$|\.py$" | head -10
ls -la /home/prd_debian/ocp_wms_core/ocp_score-main/service/ 2>/dev/null | grep -i config
cd /home/prd_debian && ./PROCESSAR_MEUS_XMLS.sh 2>&1 | head -80
curl -s http://localhost:8001/health 2>&1 || echo "API não está respondendo"
ps aux | grep -E "boxing|8001" | grep -v grep
tail -20 /home/prd_debian/mapas/out/processamento_massa/logs/processamento_20251222_180040.log | grep -A 5 "Boxing"
cd /home/prd_debian/wms-itemsboxing/src && source ../venv/bin/activate && nohup python app.py > /tmp/boxing.log 2>&1 & echo "Boxing API iniciada com PID: $!"
sleep 3 && curl -s http://localhost:8001/api/items-boxing/health/ || echo "Aguardando API iniciar..."
