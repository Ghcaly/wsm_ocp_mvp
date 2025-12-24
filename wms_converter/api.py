from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import xml.etree.ElementTree as ET

from modules.api_service import ApiService

app = FastAPI(
    title="WMS Converter API",
    description="API para conversao de XML para JSON",
    version="1.0.0"
)

service = ApiService()


@app.get("/")
async def root():
    return {
        "service": "WMS Converter API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/convert")
async def convert_xml(
    file: UploadFile = File(...),
    unique_key: Optional[str] = Form(None),
    unbcode: Optional[str] = Form(None),
    delivery_date: Optional[str] = Form(None),
    plate: Optional[str] = Form(None),
    support_point: Optional[str] = Form(None)
):
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser XML")
    
    try:
        xml_content = await file.read()
        xml_str = xml_content.decode('utf-8')
        
        overrides = {}
        if unique_key:
            overrides['unique_key'] = unique_key
        if unbcode:
            overrides['unbcode'] = unbcode
        if delivery_date:
            overrides['delivery_date'] = delivery_date
        if plate:
            overrides['plate'] = plate
        if support_point:
            overrides['support_point'] = support_point
        
        result = service.convert_xml_content(xml_str, overrides)
        
        return JSONResponse(content=result)
        
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao parsear XML: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")


@app.post("/convert/raw")
async def convert_xml_raw(
    xml_content: str = Form(...),
    unique_key: Optional[str] = Form(None),
    unbcode: Optional[str] = Form(None),
    delivery_date: Optional[str] = Form(None),
    plate: Optional[str] = Form(None),
    support_point: Optional[str] = Form(None)
):
    try:
        overrides = {}
        if unique_key:
            overrides['unique_key'] = unique_key
        if unbcode:
            overrides['unbcode'] = unbcode
        if delivery_date:
            overrides['delivery_date'] = delivery_date
        if plate:
            overrides['plate'] = plate
        if support_point:
            overrides['support_point'] = support_point
        
        result = service.convert_xml_content(xml_content, overrides)
        
        return JSONResponse(content=result)
        
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao parsear XML: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
