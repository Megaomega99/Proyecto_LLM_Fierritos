# app/services/llm_service.py
from langchain_community.llms import Ollama
from typing import List
import json
from fastapi import HTTPException

class LLMService:
    def __init__(self):
        try:
            self.llm = Ollama(model="llama2")
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail="No se pudo conectar al servicio LLM. Asegúrate de que Ollama esté corriendo."
            )

    async def generate_summary(self, content: str) -> str:
        try:
            prompt = f"Genera un resumen del siguiente texto:\n{content}"
            return self.llm.invoke(prompt)
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error al generar el resumen: {str(e)}"
            )

    async def answer_question(self, context: str, question: str) -> str:
        try:
            prompt = f"Basándote en el siguiente contexto:\n{context}\n\nResponde esta pregunta:\n{question}"
            return self.llm.invoke(prompt)
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error al responder la pregunta: {str(e)}"
            )

    async def generate_explanations(self, content: str, concepts: List[str]) -> str:
        prompt = f"""For these concepts, provide explanations from the content:

Content:
{content}

Concepts:
{json.dumps(concepts, indent=2)}

Explanations:"""
        return self.llm.invoke(prompt)