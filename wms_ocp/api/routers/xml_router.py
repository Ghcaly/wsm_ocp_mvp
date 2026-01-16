from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import xml.etree.ElementTree as ET
from ...service.palletizing_processor import PalletizingProcessor
from ...adapters.logger_instance import set_logger, clear_logger
from ...adapters.logger_system import JsonStepLogger

from pathlib import Path
import uuid

router = APIRouter(prefix="/xml", tags=["XML"])

async def request_logger_dependency():
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    filename = f"process_log_{uuid.uuid4().hex[:8]}.json"
    logger_inst = JsonStepLogger(filepath=str(data_dir / filename))
    set_logger(logger_inst)
    try:
        yield logger_inst
    finally:
        try:
            logger_inst.save()  # salva no filepath já configurado
        except Exception:
            pass
        
@router.post("/process")
async def process_xml(file: UploadFile = File(...), _logger=Depends(request_logger_dependency)):
    if file.content_type not in ("application/xml", "text/xml"):
        raise HTTPException(status_code=400, detail="Arquivo inválido")

    content = await file.read()

    try:
        ET.fromstring(content)
    except ET.ParseError:
        raise HTTPException(
            status_code=400,
            detail="Conteúdo não é um XML válido"
        )

    # run palletization using an instance (synchronous)
    try:
        processor = PalletizingProcessor(debug_enabled=True)
        result = processor.run_from_xml(content, filename=file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar o XML: {str(e)}"
        )
    return {
        "filename": file.filename,
        "bytes": len(content),
        "message": "XML válido"
    }
