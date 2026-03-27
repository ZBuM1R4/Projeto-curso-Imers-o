import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


FALLBACK_MESSAGE = (
    "Análise global por IA indisponível no momento. "
    "O relatório foi gerado com os demais critérios normalmente."
)


def analyze_full_transcription_with_gemini(transcription: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return {
            "disponivel": False,
            "mensagem": FALLBACK_MESSAGE,
            "analise": "",
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Você é um avaliador de comunicação oral em português.

Analise a transcrição abaixo como um todo, considerando:
- vícios de linguagem
- repetições
- clareza da construção frasal
- fluidez
- qualidade geral da comunicação

Regras:
- faça uma análise curta, objetiva e profissional
- não reescreva o texto
- não corrija a transcrição
- não use markdown
- organize a resposta em 5 blocos curtos:
1. Vícios de linguagem
2. Repetição
3. Clareza e construção
4. Fluidez
5. Leitura geral

Transcrição:
{transcription}
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        return {
            "disponivel": True,
            "mensagem": "Análise global por IA executada com sucesso.",
            "analise": response.text.strip(),
        }

    except Exception as e:
        return {
            "disponivel": False,
            "mensagem": f"{FALLBACK_MESSAGE} | Erro técnico: {str(e)}",
            "analise": "",
        }