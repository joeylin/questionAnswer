import asyncio
import logging
from typing import AsyncIterable, Awaitable

from langchain.chat_models import ChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import BSHTMLLoader, PyPDFLoader, CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()
print(os.environ["OPENAI_API_KEY"])
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)


def get_documents(filepath: str, loader_type: str):
    if loader_type.lower() == 'html':
        return BSHTMLLoader(filepath).load()
    elif loader_type.lower() == 'pdf':
        return PyPDFLoader(filepath).load()
    elif loader_type.lower() == 'csv':
        return CSVLoader(filepath).load()
    else:
        raise ValueError(f'Unsupported filetype {loader_type}')


class DocumentIngest:
    vectordb: Chroma
    name: str
    embedding: Embeddings

    def __init__(self, persist_directory: str = ".vector_persist", name: str = "default") -> None:
        embedding = OpenAIEmbeddings()
        self.name = name
        self.vectordb = Chroma(
            collection_name=name,
            persist_directory=persist_directory,
            embedding_function=embedding
        )

    def add_file(self, filepath: str, loader_type: str) -> None:
        documents = get_documents(filepath, loader_type)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        self.vectordb.add_documents(texts)
        self.vectordb.persist()
