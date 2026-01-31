import io
from pydantic import BaseModel
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated
#from services.geminiService import generateSummary, countRedactions, performPrivacyValidation
#from services.pdfService import extractTextFromPdf, generateRedactedPdf
#from services.ollamaService import checkOllamaConnection, sanitizeWithOllama, assessRiskWithOllama, screenPrivacyRisks, DEFAULT_OLLAMA_CONFIG, OllamaConfig

app = FastAPI()
router = APIRouter()

class Config(BaseModel):
    theme: str
    notifications: bool

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/upload/pdf")
async def upload_pdf(file: Annotated[UploadFile, File(description="Upload a PDF")]):
    # Validate file type manually if needed
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Process file content
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}


@app.get("/download/report")
async def get_report():
    # Create data using Pydantic
    config = Config(theme="dark", notifications=True)
    
    # Dump Pydantic model to a JSON string, then to bytes
    json_data = config.model_dump_json()
    stream = io.BytesIO(json_data.encode())
    
    return StreamingResponse(
        stream, 
        media_type="application/json", 
        headers={"Content-Disposition": "attachment; filename=report.json"}
    )

@app.get("/download/dictionary")
async def download_dictionary():
    # Create data using Pydantic
    config = Config(theme="dark", notifications=True)
    
    # Dump Pydantic model to a JSON string, then to bytes
    json_data = config.model_dump_json()
    stream = io.BytesIO(json_data.encode())
    
    return StreamingResponse(
        stream, 
        media_type="application/json", 
        headers={"Content-Disposition": "attachment; filename=dictionary.json"}
    )

@app.get("/download/risk-report")
async def download_risk_report():
    # Create data using Pydantic
    config = Config(theme="dark", notifications=True)
    
    # Dump Pydantic model to a JSON string, then to bytes
    json_data = config.model_dump_json()
    stream = io.BytesIO(json_data.encode())
    
    return StreamingResponse(
        stream, 
        media_type="application/json", 
        headers={"Content-Disposition": "attachment; filename=risk-report.json"}
    )
app.include_router(router, prefix="/api")