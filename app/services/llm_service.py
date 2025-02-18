# app/services/llm_service.py
from langchain.llms import Ollama
from typing import List
import json

class LLMService:
    def __init__(self):
        self.llm = Ollama(model="llama2")

    async def generate_summary(self, content: str) -> str:
        prompt = f"""Please provide a concise summary of the following text:

{content}

Summary:"""
        return self.llm.invoke(prompt)

    async def answer_question(self, content: str, question: str) -> str:
        prompt = f"""Based on this content:

{content}

Answer this question: {question}"""
        return self.llm.invoke(prompt)

    async def generate_explanations(self, content: str, concepts: List[str]) -> str:
        prompt = f"""For these concepts, provide explanations from the content:

Content:
{content}

Concepts:
{json.dumps(concepts, indent=2)}

Explanations:"""
        return self.llm.invoke(prompt)