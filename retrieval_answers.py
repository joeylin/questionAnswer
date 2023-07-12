import asyncio
from typing import Awaitable, AsyncIterable

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from default_prompt import WISDOM_QA_PROMPT, WISDOM_CONDENSE_QUESTION_PROMPT


class RetrievalAnswer:
    vectordb: Chroma
    name: str
    llm: ChatOpenAI
    stream_llm: ChatOpenAI
    callback: AsyncIteratorCallbackHandler()

    def __init__(self, persist_directory: str = ".vector_persist", name: str = "default") -> None:
        embedding = OpenAIEmbeddings()
        self.name = name
        self.callback = AsyncIteratorCallbackHandler()
        self.vectordb = Chroma(
            collection_name=name,
            persist_directory=persist_directory,
            embedding_function=embedding
        )
        self.llm = ChatOpenAI(verbose=True,
                              temperature=0)
        self.stream_llm = ChatOpenAI(streaming=True,
                                     verbose=True,
                                     callbacks=[self.callback],
                                     temperature=0)

    async def stream(self, query: str, history: []) -> AsyncIterable[str]:
        retriever = self.vectordb.as_retriever()
        qa = ConversationalRetrievalChain.from_llm(llm=self.stream_llm,
                                                   retriever=retriever,
                                                   condense_question_llm=self.llm,
                                                   condense_question_prompt=WISDOM_CONDENSE_QUESTION_PROMPT,
                                                   combine_docs_chain_kwargs={"prompt": WISDOM_QA_PROMPT},
                                                   verbose=True,
                                                   max_tokens_limit=4000,
                                                   return_source_documents=True)

        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
            try:
                await fn
            except Exception as e:
                print(f"Caught exception: {e}")
            finally:
                # Signal the aiter to stop.
                event.set()

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            qa.acall({"question": query, "chat_history": history}),
            self.callback.done),
        )

        async for token in self.callback.aiter():
            yield f"{token}"

        await task

    def query(self, query: str, history: []) -> str:
        retriever = self.vectordb.as_retriever()
        qa = ConversationalRetrievalChain.from_llm(llm=self.llm,
                                                   retriever=retriever,
                                                   verbose=True,
                                                   condense_question_llm=self.llm,
                                                   return_source_documents=True)
        result = qa({"question": query, "chat_history": history})
        return result["answer"]