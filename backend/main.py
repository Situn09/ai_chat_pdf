from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import extract_text_from_pdf
import os



app = FastAPI()

# Model for question
class Question(BaseModel):
    question: str

# Directory where uploaded files will be saved
UPLOAD_DIRECTORY = "./uploaded_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize the question answering pipeline from Hugging Face
# "OpenAssistant/oasst-sft-1-pythia-12b", "bigscience/bloomz-7b1" , "google/flan-ul2" 
qa_pipeline = pipeline("question-answering")

@app.get("/")
async def root():
    return {"message": "Hello World"}

# qa_pipeline = pipeline("question-answering", model="distilbert/distilbert-base-cased-distilled-squad", tokenizer="google-bert/bert-base-cased")
# qa_pipeline=pipeline("text-generation", model="OpenAssistant/oasst-sft-1-pythia-12b")
# qa_pipeline=pipeline("question-answering", model="PhucDanh/Bartpho-fine-tuning-model-for-question-answering")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    file_location = os.path.join(UPLOAD_DIRECTORY, "uploaded.pdf")
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    return JSONResponse(content={"filename": file.filename, "message": "File uploaded successfully."})

# Endpoint for question answering
@app.post("/ask-question/")
async def ask_question(question:Question):
    # Extract text from the PDF
    pdf_text = extract_text_from_pdf("./uploaded_files/uploaded.pdf")  # Assuming the file is uploaded as 'uploaded.pdf'
    
    # Use the Hugging Face pipeline to answer the question
    result = qa_pipeline(question=question.question, context=pdf_text)
    
    return JSONResponse(content={"answer": result['answer']})

    

# To run the app, use: `uvicorn your_script_name:app --reload`

