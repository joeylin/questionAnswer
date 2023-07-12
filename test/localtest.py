import asyncio

from dotenv import load_dotenv

from ingest import QuestionAnswer

load_dotenv()

qa = QuestionAnswer(name="test")


async def main():
    async for token in qa.stream("What is Azure?", []):
        print(token)


asyncio.run(main())
