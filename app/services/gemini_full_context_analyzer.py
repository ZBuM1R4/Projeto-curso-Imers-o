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

Avalie a transcrição inteira e dê notas de 0 a 1.
As notas devem ser severas e proporcionais à frequência dos problemas.

Retorne apenas JSON válido neste formato:

{{
  "metricas": {{
    "controle_linguagem": 0.0,
    "clareza": 0.0,
    "formalidade": 0.0,
    "fluidez": 0.0,
    "qualidade_comunicacao": 0.0
  }},
  "analise": "análise objetiva, com os principais problemas e o impacto na comunicação"
}}

Critérios:
- controle_linguagem: penalize vícios de linguagem, muletas, repetição excessiva, termos soltos e fala desorganizada.
- clareza: penalize frases confusas, ideias mal conectadas, erros gramaticais e falta de objetividade.
- formalidade: penalize gírias, coloquialidade excessiva, improviso excessivo e tom pouco profissional.
- fluidez: penalize hesitações, pausas, cortes, travamentos e quebras de raciocínio.
- qualidade_comunicacao: avalie segurança, organização, maturidade, objetividade e impacto geral.

Escala obrigatória:
- 0.00 a 0.20 = crítico, comunicação muito comprometida.
- 0.21 a 0.40 = ruim, muitos problemas relevantes.
- 0.41 a 0.60 = regular, problemas frequentes.
- 0.61 a 0.80 = bom, poucos problemas.
- 0.81 a 1.00 = excelente, fala clara, segura e bem estruturada.

Regras:
- se houver muitos vícios, repetições ou fala confusa, controle_linguagem deve ser no máximo 0.35.
- se as ideias forem difíceis de entender, clareza deve ser no máximo 0.40.
- se houver travamentos frequentes, fluidez deve ser no máximo 0.40.
- se a fala parecer improvisada, insegura ou desorganizada, qualidade_comunicacao deve ser no máximo 0.40.
- não dê notas altas para falas apenas compreensíveis.
- seja rigoroso, não suavize falhas.
- a análise deve citar problemas concretos percebidos na transcrição.
- não use markdown.
- não escreva nada fora do JSON.

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