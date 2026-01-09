#!/usr/bin/env python3
"""
Wrapper para iniciar api_server.py corretamente
Resolve problemas de imports relativos
"""

import os
import sys

# Adicionar path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.environ["PYTHONPATH"] = script_dir

# Mudar diretório
os.chdir(script_dir)

# Importar e executar
import api_server
