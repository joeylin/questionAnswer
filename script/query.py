from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import BSHTMLLoader
from langchain.embeddings import TensorflowHubEmbeddings, SentenceTransformerEmbeddings, OpenAIEmbeddings
import requests
import os

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer

os.environ["OPENAI_API_KEY"] = "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"

url = 'https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/notion.html'
path = '../docs/'

response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"请求失败，状态码：{response.status_code}")
with open(path + 'query.html', 'wb+') as f:
    f.write(response.content)

loader = BSHTMLLoader(path + 'query.html')
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

# 使用SentenceTransformer做embedding
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# if device != 'cuda':
#     print(f"You are using {device}. This is much slower than using "
#           "a CUDA-enabled GPU. If on Colab you can change this by "
#           "clicking Runtime > Change runtime type > GPU.")
#
# model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

db = Chroma.from_documents(texts, embeddings)
retriever = db.as_retriever()
qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=retriever)

query = "what is Notion"
print(qa.run(query))
