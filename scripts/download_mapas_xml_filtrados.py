#!/usr/bin/env python3
"""
Baixa apenas os XML dos mapas desejados do container Azure para uma pasta local.

Baseado no script original de download, mas filtrando pelos IDs de mapa.
Requisitos: pip install azure-storage-blob
"""

from azure.storage.blob import ContainerClient, BlobClient
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys

# --- Configurações -----------------------------------------------------------
# URL SAS com permissão de leitura
SAS_URL = (
    "https://stwmsprdbrs.blob.core.windows.net/ocp"
    "?sp=rl&st=2025-11-18T13:56:03Z&se=2026-06-01T22:11:03Z&spr=https"
    "&sv=2024-11-04&sr=c&sig=preLCG2Qyp1aResymdpbKEYEpKo7iXNOJGKTb8YSliE%3D"
)
# Prefixo dentro do container (ajuste se necessário, ex.: "out/" ou "in/")
SOURCE_PREFIX = ""
# Lista de mapas que queremos baixar
TARGET_MAPAS = {"622247", "622273", "622704"}
# Concurrency e limites
MAX_FILES = 13000
CONCURRENCY = 8

# Destino local (abaixo da raiz do projeto)
BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_DIR = BASE_DIR / "mapas_xml_saidas" / "from_blob"

# --- Helpers ----------------------------------------------------------------

def build_blob_url(container_sas_url, blob_name):
    base, query = container_sas_url.split("?", 1)
    if not base.endswith("/"):
        base += "/"
    return f"{base}{blob_name}?{query}"


def matches_target(blob_name: str) -> bool:
    """Retorna True se o blob corresponder a algum mapa alvo e for XML."""
    if not blob_name.lower().endswith(".xml"):
        return False
    return any(mapa in blob_name for mapa in TARGET_MAPAS)


def download_blob(container_sas_url, blob_name, local_path: Path):
    local_path.parent.mkdir(parents=True, exist_ok=True)
    blob_url = build_blob_url(container_sas_url, blob_name)
    blob_client = BlobClient.from_blob_url(blob_url)
    with open(local_path, "wb") as f:
        stream = blob_client.download_blob()
        f.write(stream.readall())
    return str(local_path)


def main():
    if not TARGET_MAPAS:
        print("Nenhum mapa definido em TARGET_MAPAS. Ajuste a lista e rode novamente.")
        sys.exit(1)

    container_client = ContainerClient.from_container_url(SAS_URL)

    blobs = []
    for i, blob in enumerate(container_client.list_blobs(name_starts_with=SOURCE_PREFIX)):
        if i >= MAX_FILES:
            break
        if matches_target(blob.name):
            relative_name = blob.name.split("/")[-1]
            local_path = LOCAL_DIR / relative_name
            blobs.append((blob.name, local_path))

    if not blobs:
        print(f"Nenhum blob encontrado em '{SOURCE_PREFIX}' para os mapas {sorted(TARGET_MAPAS)}.")
        return

    print(f"Pasta do script: {Path(__file__).resolve().parent}")
    print(f"Baixando {len(blobs)} arquivos para '{LOCAL_DIR}'...\n")

    errors = []
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = {executor.submit(download_blob, SAS_URL, src, dst): (src, dst) for src, dst in blobs}
        for future in as_completed(futures):
            src, dst = futures[future]
            try:
                future.result()
            except Exception as e:
                errors.append((src, str(e)))

    print("\nDownload concluído!")
    if errors:
        print(f"Erros em {len(errors)} arquivos (mostrando até 10):")
        for src, err in errors[:10]:
            print(f"- {src}: {err}")


if __name__ == "__main__":
    main()
