from fastapi import FastAPI, UploadFile, File
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import json

app = FastAPI()

def preprocces_json(data):
    chat_text = "\n".join([msg["text"] for msg in data])
    input_text = "Summarize the following conversation. Give mainly the opinions of the people:\n" + chat_text
    return input_text

@app.post("/summarize/")
async def summarize(file: UploadFile = File(...), model_path: str = "Testing/bartsummarizer"):
    contents = await file.read()
    data = json.loads(contents)
    input_text = preprocces_json(data)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)
    summary = summarizer(
        input_text,
        max_length=248,
        min_length=50,
        do_sample=True,
        num_beams=4
    )[0]["summary_text"]
    return {"summary": summary}

# uvicorn api:app --reload
# http://127.0.0.1:8000/docs