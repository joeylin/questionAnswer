from langchain import PromptTemplate

_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
WISDOM_CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

prompt_template = """I want you to act as a document that I am having a conversation with. Your name is "AI Assistant". You will provide me with answers from the given info. If the answer is not included, say exactly "I'm sorry, I don't have the information you're looking for, please contact customer support." and stop after that. Refuse to answer any question not about the info. Never break character.

{context}

Question: {question}
Helpful Answer:"""
WISDOM_QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
