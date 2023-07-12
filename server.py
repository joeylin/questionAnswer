from typing import List

import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from retrieval_answers import RetrievalAnswer

load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")


class QueryRequest(BaseModel):
    """Request body for streaming."""
    question: str
    prompt: str
    messages: List[str]


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/stream")
def stream(body: QueryRequest):
    print(body)
    qa = RetrievalAnswer(name="test", prompt=body.prompt)
    return StreamingResponse(qa.stream(body.question, body.messages), media_type="text/plain")


@app.post("/query")
def query(body: QueryRequest):
    qa = RetrievalAnswer(name="test", prompt=body.prompt)
    return qa.query(body.question, body.messages)


if __name__ == "__main__":
    uvicorn.run(host="127.0.0.1", port=5002, app=app)
