#!/usr/bin/env python3
"""
FastAPI - API completa para processamento de mapas

Endpoints:
    POST /process-xml - Upload e processamento completo de XML
    POST /process-json - Processamento a partir de JSON
    GET /result/{map_number} - Baixar resultado TXT
    GET /health - Health check
    GET / - Documentação

Uso:
    source /home/wms_core/wms_venv/bin/activate
    cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main
    uvicorn api_fastapi:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import json
import sys
import requests
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Adiciona path
sys.path.insert(0, str(Path(__file__).parent))

from service.palletizing_processor import PalletizingProcessor
from service.config_generator import ConfigGenerator

# Configuração
app = FastAPI(
    title="API de Paletização OCP",
    description="API completa para processamento de mapas XML com paletização",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
WMS_CONVERTER_URL = "http://localhost:8002/convert"
OUTPUT_DIR = Path("/tmp/ocp_results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ProcessResponse(BaseModel):
    success: bool
    map_number: int
    message: str
    pallets_count: int
    units_palletized: int
    total_weight: float
    txt_file: str
    json_file: str
    config_file: str
    processing_time: float


class ErrorResponse(BaseModel):
    success: bool
    error: str
    detail: Optional[str] = None


@app.get("/")
async def root():
    """Documentação da API"""
    return {
        "service": "API de Paletização OCP (FastAPI)",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "POST /process-xml": "Upload e processamento completo de XML",
            "POST /process-json": "Processamento a partir de JSON convertido",
            "GET /result/{map_number}": "Download do resultado TXT",
            "GET /health": "Health check",
            "GET /docs": "Documentação interativa Swagger"
        },
        "workflow": [
            "1. Upload XML via POST /process-xml",
            "2. Sistema converte XML → JSON (WMS Converter)",
            "3. Gera configuração automaticamente",
            "4. Executa paletização (51 regras)",
            "5. Gera saída TXT profissional",
            "6. Retorna URLs para download"
        ]
    }


@app.get("/health")
async def health():
    """Health check"""
    try:
        # Verifica se WMS Converter está disponível
        response = requests.get("http://localhost:8002/", timeout=2)
        wms_converter_ok = response.status_code == 200
    except:
        wms_converter_ok = False
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "ok",
            "wms_converter": "ok" if wms_converter_ok else "unavailable"
        }
    }


@app.post("/process-xml", response_model=ProcessResponse)
async def process_xml(file: UploadFile = File(...)):
    """
    Upload e processamento completo de arquivo XML
    
    Args:
        file: Arquivo XML do mapa
        
    Returns:
        Resultado do processamento com estatísticas e caminhos dos arquivos
    """
    start_time = datetime.now()
    
    try:
        # Valida tipo de arquivo
        if not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser XML")
        
        logger.info(f"📥 Recebendo arquivo: {file.filename}")
        
        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_xml_path = Path(tmp_file.name)
        
        logger.info(f"💾 Arquivo salvo temporariamente: {tmp_xml_path}")
        
        # STEP 1: Converte XML → JSON via WMS Converter
        logger.info("🔄 STEP 1: Convertendo XML → JSON")
        
        with open(tmp_xml_path, 'rb') as f:
            files = {'file': (file.filename, f, 'application/xml')}
            response = requests.post(WMS_CONVERTER_URL, files=files, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao converter XML: {response.text}"
            )
        
        json_data = response.json()
        map_number = json_data.get('MapNumber', 0)
        
        logger.info(f"✅ JSON convertido - Mapa: {map_number}")
        
        # Salva JSON
        json_file = OUTPUT_DIR / f"{map_number}_input.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # STEP 2: Gera configuração
        logger.info("⚙️  STEP 2: Gerando configuração")
        
        config_generator = ConfigGenerator()
        config_file = OUTPUT_DIR / f"config_{map_number}.json"
        config_generator.generate_config_file(
            input_file=str(json_file),
            output_file=str(config_file),
            overwrite=True
        )
        
        logger.info(f"✅ Configuração gerada: {config_file}")
        
        # STEP 3 e 4: Processa paletização e gera TXT
        logger.info("🎯 STEP 3-4: Processando paletização e gerando TXT")
        
        processor = PalletizingProcessor()
        result = processor.run_complete_palletizing_process(
            config_file=str(config_file),
            data_file=str(json_file),
            output_dir=str(OUTPUT_DIR)
        )
        
        # Extrai estatísticas
        context = result.get('context')
        pallets_count = len(context.MountedSpaces) if context else 0
        
        # Conta unidades paletizadas
        units_palletized = 0
        total_weight = 0.0
        if context and context.MountedSpaces:
            for space in context.MountedSpaces:
                for container in space.Containers:
                    for product in container.Products:
                        units_palletized += product.Amount
                        total_weight += float(product.Weight or 0)
        
        # Arquivos de saída
        txt_file = OUTPUT_DIR / f"{map_number}-ocp-map.txt"
        json_output = OUTPUT_DIR / f"{map_number}-ocp-map.json"
        
        # Tempo de processamento
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Remove arquivo temporário
        tmp_xml_path.unlink()
        
        logger.info(f"✅ Processamento concluído em {processing_time:.2f}s")
        logger.info(f"   📦 {pallets_count} paletes, {units_palletized} unidades, {total_weight:.2f}kg")
        
        return ProcessResponse(
            success=True,
            map_number=map_number,
            message=f"Processamento concluído com sucesso",
            pallets_count=pallets_count,
            units_palletized=units_palletized,
            total_weight=total_weight,
            txt_file=str(txt_file),
            json_file=str(json_output),
            config_file=str(config_file),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-json")
async def process_json(data: Dict[str, Any]):
    """
    Processamento a partir de JSON já convertido
    
    Args:
        data: JSON do mapa já convertido
        
    Returns:
        Resultado do processamento
    """
    start_time = datetime.now()
    
    try:
        map_number = data.get('MapNumber', 0)
        
        if not map_number:
            raise HTTPException(status_code=400, detail="MapNumber não encontrado no JSON")
        
        logger.info(f"🔄 Processando JSON do mapa: {map_number}")
        
        # Salva JSON
        json_file = OUTPUT_DIR / f"{map_number}_input.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Gera configuração
        logger.info("⚙️  Gerando configuração")
        config_generator = ConfigGenerator()
        config_file = OUTPUT_DIR / f"config_{map_number}.json"
        config_generator.generate_config_file(
            input_file=str(json_file),
            output_file=str(config_file),
            overwrite=True
        )
        
        # Processa paletização
        logger.info("🎯 Processando paletização")
        processor = PalletizingProcessor()
        result = processor.run_complete_palletizing_process(
            config_file=str(config_file),
            data_file=str(json_file),
            output_dir=str(OUTPUT_DIR)
        )
        
        # Extrai estatísticas
        context = result.get('context')
        pallets_count = len(context.MountedSpaces) if context else 0
        
        units_palletized = 0
        total_weight = 0.0
        if context and context.MountedSpaces:
            for space in context.MountedSpaces:
                for container in space.Containers:
                    for product in container.Products:
                        units_palletized += product.Amount
                        total_weight += float(product.Weight or 0)
        
        txt_file = OUTPUT_DIR / f"{map_number}-ocp-map.txt"
        json_output = OUTPUT_DIR / f"{map_number}-ocp-map.json"
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Processamento concluído em {processing_time:.2f}s")
        
        return ProcessResponse(
            success=True,
            map_number=map_number,
            message="Processamento concluído com sucesso",
            pallets_count=pallets_count,
            units_palletized=units_palletized,
            total_weight=total_weight,
            txt_file=str(txt_file),
            json_file=str(json_output),
            config_file=str(config_file),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/result/{map_number}")
async def get_result(map_number: int):
    """
    Download do arquivo TXT resultado
    
    Args:
        map_number: Número do mapa
        
    Returns:
        Arquivo TXT para download
    """
    txt_file = OUTPUT_DIR / f"{map_number}-ocp-map.txt"
    
    if not txt_file.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Resultado não encontrado para mapa {map_number}"
        )
    
    return FileResponse(
        path=txt_file,
        filename=f"{map_number}-ocp-map.txt",
        media_type="text/plain"
    )


@app.get("/json/{map_number}")
async def get_json(map_number: int):
    """
    Download do arquivo JSON resultado
    
    Args:
        map_number: Número do mapa
        
    Returns:
        Arquivo JSON para download
    """
    json_file = OUTPUT_DIR / f"{map_number}-ocp-map.json"
    
    if not json_file.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"JSON não encontrado para mapa {map_number}"
        )
    
    return FileResponse(
        path=json_file,
        filename=f"{map_number}-ocp-map.json",
        media_type="application/json"
    )


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 API FastAPI - Paletização OCP")
    print("=" * 70)
    print(f"📍 URL: http://localhost:8000")
    print(f"📖 Docs: http://localhost:8000/docs")
    print(f"📂 Output: {OUTPUT_DIR}")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
