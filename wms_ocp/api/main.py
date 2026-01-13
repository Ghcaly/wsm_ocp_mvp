from fastapi import FastAPI 
from .routers.xml_router import router as xml_router

app = FastAPI()
app.include_router(xml_router)
