from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import BSHTMLLoader, PyPDFLoader, CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()
print(os.environ["OPENAI_API_KEY"])


def get_documents(filepath: str, loader_type: str):
    if loader_type.lower() == 'html':
        return BSHTMLLoader(filepath).load()
    elif loader_type.lower() == 'pdf':
        return PyPDFLoader(filepath).load()
    elif loader_type.lower() == 'csv':
        return CSVLoader(filepath).load()
    else:
        raise ValueError(f'Unsupported filetype {loader_type}')


class QuestionAnswer:
    vectordb: Chroma
    name: str
    llm: OpenAI

    def __init__(self, persist_directory: str = ".vector_persist", name: str = "default") -> None:
        embedding = OpenAIEmbeddings()
        self.name = name
        self.vectordb = Chroma(
            collection_name=name,
            persist_directory=persist_directory,
            embedding_function=embedding
        )
        self.llm = OpenAI()

    def add_file(self, filepath: str, loader_type: str) -> None:
        documents = get_documents(filepath, loader_type)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        self.vectordb.add_documents(texts)
        self.vectordb.persist()

    def query(self, query: str) -> str:
        retriever = self.vectordb.as_retriever()
        retriever.get_relevant_documents("总结下这篇文章的主要观点")
        qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=retriever)
        return qa.run(query)
