import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


FALLBACK_MESSAGE = (
    "Análise global por IA indisponível no momento. "
    "O relatório foi gerado com os demais critérios normalmente."
)


def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Não foi possível localizar um JSON válido na resposta da IA.")

    return json.loads(text[start:end + 1])


def analyze_full_transcription_with_gemini(transcription: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return {
            "disponivel": False,
            "mensagem": FALLBACK_MESSAGE,
            "analise": "",
            "metricas": {},
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Você é um avaliador rigoroso de comunicação oral em português.

Analise a transcrição como um todo e avalie a QUALIDADE REAL da comunicação.

Retorne APENAS JSON no formato:

{{
  "metricas": {{
    "controle_linguagem": 0.0,
    "clareza": 0.0,
    "formalidade": 0.0,
    "fluidez": 0.0,
    "qualidade_comunicacao": 0.0
  }},
  "analise": "texto curto explicando os principais problemas"
}}

Critérios de avaliação:

- controle_linguagem:
  penalize vícios de linguagem, muletas e fala desorganizada

- clareza:
  penalize frases mal construídas, erros gramaticais e confusão

- formalidade:
  penalize linguagem excessivamente informal ou pouco profissional

- fluidez:
  penalize pausas, hesitação e quebra de raciocínio

- qualidade_comunicacao:
  avalie o nível geral da fala:
  clareza de ideias, segurança, objetividade e maturidade

Escala:
- 0 = muito ruim
- 1 = excelente

IMPORTANTE:
- seja crítico (não seja permissivo)
- não suavize erros
- se houver muitos problemas, as notas devem ser baixas
- coerência entre métricas e análise é obrigatória
- não use markdown
- não escreva nada fora do JSON

Transcrição:
{transcription}
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        parsed = extract_json(response.text)

        return {
            "disponivel": True,
            "mensagem": "Análise global por IA executada com sucesso.",
            "analise": parsed.get("analise", "").strip(),
            "metricas": parsed.get("metricas", {}),
        }

    except Exception as e:
        return {
            "disponivel": False,
            "mensagem": f"{FALLBACK_MESSAGE} | Erro técnico: {str(e)}",
            "analise": "",
            "metricas": {},
        }