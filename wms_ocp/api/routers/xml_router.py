from fastapi import APIRouter, UploadFile, File, HTTPException
import xml.etree.ElementTree as ET
from ...service.palletizing_processor import PalletizingProcessor

router = APIRouter(prefix="/xml", tags=["XML"])

@router.post("/process")
async def process_xml(file: UploadFile = File(...)):
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
