import logging
from typing import List

from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from dotenv import load_dotenv
import os
import oss2

from langchain.document_loaders import (
    BSHTMLLoader,
    CSVLoader,
    EverNoteLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
)

load_dotenv()
print(os.environ["OPENAI_API_KEY"])
endpoint = os.environ['ALIYUN_OSS_ENDPOINT']
access_key_id = os.environ['ALIYUN_OSS_ACCESS_KEY_ID']
access_key_secret = os.environ['ALIYUN_OSS_ACCESS_KEY_SECRET']
bucket_name = os.environ['ALIYUN_OSS_BUCKET_NAME']

# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}


def load_single_document(file_path: str) -> List[Document]:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()
    else:
        raise ValueError(f'Unsupported filetype {file_path}')


def download_oss_document(oss_path: str) -> str:
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
    if not bucket.object_exists(oss_path):
        raise ValueError(f'not exists oss file: {oss_path}')

    local_path = "./docs" + oss_path
    bucket.get_object_to_file(oss_path, local_path)
    print("downloaded file to " + local_path + " successfully")
    return local_path


def process_document(filepath: str) -> List[Document]:
    documents = load_single_document(filepath)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    texts = text_splitter.split_documents(documents)
    return texts


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

    def ingest_local_file(self, filepath: str) -> None:
        texts = process_document(filepath)
        self.vectordb.add_documents(texts)
        self.vectordb.persist()

    def ingest_oss_file(self, filepath: str) -> None:
        local_path = download_oss_document(filepath)
        self.ingest_local_file(local_path)