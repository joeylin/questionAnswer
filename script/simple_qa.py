from langchain import OpenAI
from langchain.document_loaders import BSHTMLLoader
from langchain.indexes import VectorstoreIndexCreator
import requests
import os

from langchain.llms import GooglePalm

os.environ["OPENAI_API_KEY"] = "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"

url = 'https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/notion.html'
path = '../docs/'

response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"请求失败，状态码：{response.status_code}")
with open(path + 'main.html', 'wb+') as f:
    f.write(response.content)

loader = BSHTMLLoader(path + 'main.html')
index = VectorstoreIndexCreator().from_loaders([loader])

query = "what is Notion"
result = index.query(question=query, llm=OpenAI())
print(result)
