"""
Helper para importar bliblioteca do binpacking enquanto ela ainda não está disponível como pacote.
"""
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.joinpath("binpacking").resolve()))
