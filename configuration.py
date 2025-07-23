from langchain_openai import ChatOpenAI


from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


LLM_ = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0.7,
    openai_api_key=api_key
)

