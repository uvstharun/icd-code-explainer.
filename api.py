from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from explainer import explain_icd_code, ICDResult

load_dotenv()

app = FastAPI(title="ICD Code Explainer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClinicalRequest(BaseModel):
    description: str

response_cache = {}

@app.get("/")
def root():
    return {"status": "ICD Code Explainer API is running"}

@app.post("/code", response_model=ICDResult)
def code_description(request: ClinicalRequest):
    if request.description in response_cache:
        return response_cache[request.description]

    result = explain_icd_code(request.description)
    response_cache[request.description] = result
    return result