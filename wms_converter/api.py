from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
from wms_converter.modules import XmlConverter

app = FastAPI(title="WMS Converter")

@app.post("/convert")
async def convert_xml(
    file: UploadFile = File(...),
    unique_key: str = None,
    unbcode: str = None,
    delivery_date: str = None,
    plate: str = None,
    support_point: str = None,
):
    if file.content_type not in ("application/xml", "text/xml"):
        raise HTTPException(status_code=400, detail="Arquivo inválido")
    content = await file.read()

    # salvar input temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as f_in:
        f_in.write(content)
        in_path = f_in.name

    # preparar arquivo de saída temporário
    fd_out, out_path = tempfile.mkstemp(suffix=".json")
    os.close(fd_out)

    overrides = {}
    if unique_key: overrides["unique_key"] = unique_key
    if unbcode: overrides["unbcode"] = unbcode
    if delivery_date: overrides["delivery_date"] = delivery_date
    if plate: overrides["plate"] = plate
    if support_point: overrides["support_point"] = support_point

    try:
        converter = XmlConverter()
        result = converter.convert(in_path, out_path, **overrides)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try: os.remove(in_path)
        except: pass
        try: os.remove(out_path)
        except: pass

    return result