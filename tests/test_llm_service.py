import pytest
import asyncio
from app.services.llm_service import LLMService
from fastapi import HTTPException
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def llm_service():
    try:
        return LLMService()
    except Exception as e:
        logger.error(f"Error al inicializar LLMService: {e}")
        pytest.skip(f"No se pudo inicializar LLMService: {str(e)}")

@pytest.mark.asyncio
async def test_generate_summary(llm_service):
    # Texto de prueba
    content = """
    Los modelos de lenguaje grande (LLM) son sistemas de inteligencia artificial 
    diseñados para entender y generar texto en lenguaje natural. Estos modelos 
    se entrenan con grandes cantidades de datos y pueden realizar diversas tareas 
    como traducción, resumen y respuesta a preguntas.
    """
    
    try:
        summary = await llm_service.generate_summary(content)
        assert isinstance(summary, str)
        assert len(summary) > 0
        print(f"Resumen generado: {summary}")
    except HTTPException as e:
        pytest.fail(f"Error al generar el resumen: {e.detail}")

@pytest.mark.asyncio
async def test_answer_question(llm_service):
    context = """
    Python es un lenguaje de programación de alto nivel, interpretado y 
    de propósito general. Fue creado por Guido van Rossum y lanzado 
    por primera vez en 1991.
    """
    question = "¿Quién creó Python?"
    
    try:
        answer = await llm_service.answer_question(context, question)
        assert isinstance(answer, str)
        assert len(answer) > 0
        print(f"Respuesta: {answer}")
    except HTTPException as e:
        pytest.fail(f"Error al responder la pregunta: {e.detail}")

@pytest.mark.asyncio
async def test_generate_explanations(llm_service):
    content = """
    La programación orientada a objetos (POO) es un paradigma de programación
    que organiza el código en objetos que contienen datos y código. Los objetos
    tienen atributos que definen sus propiedades y métodos que definen su comportamiento.
    La herencia permite que una clase herede propiedades y métodos de otra clase.
    """
    concepts = ["POO", "herencia", "objetos"]
    
    try:
        explanations = await llm_service.generate_explanations(content, concepts)
        assert isinstance(explanations, str)
        assert len(explanations) > 0
        print(f"Explicaciones: {explanations}")
    except HTTPException as e:
        pytest.fail(f"Error al generar explicaciones: {e.detail}")

if __name__ == "__main__":
    asyncio.run(test_generate_summary(LLMService()))
    asyncio.run(test_answer_question(LLMService()))
    asyncio.run(test_generate_explanations(LLMService()))