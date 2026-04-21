# Análise de Comunicação por Vídeo

Projeto em Python para análise de comunicação a partir de vídeos, com foco em identificação de padrões como pausas, vícios de linguagem e repetição de termos.

## 🚀 Funcionalidades (MVP)

- Upload de vídeo via interface web
- Pré-visualização do vídeo
- Transcrição automática (Whisper)
- Análise global da comunicação utilizando IA (Gemini)
- Detecção de vícios de linguagem (ex: "né", "então", "assim")
- Análise de pausas e silêncio
- Identificação de termos mais recorrentes
- Marcação visual da transcrição (vícios e termos recorrentes)
- Alternância entre transcrição limpa e anotada
- Interface com Streamlit

## 🧠 Tecnologias utilizadas

- Python
- Streamlit
- OpenAI Whisper
- FFmpeg
- WebRTC VAD

## ⚙️ Requisitos

- Python 3.10+
- FFmpeg instalado e configurado no PATH

## 📂 Estrutura do projeto

```
├── app/
│   ├── ui/           # interface Streamlit
│   │   └── dashboard.py
│   ├── services/     # lógica de análise
│   └── utils/        # utilitários
├── data/
│   ├── input/
│   ├── temp/
│   └── output/
├── tests/
├── utils/
```

## ▶️ Como rodar o projeto

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente

```bash
source .venv/Scripts/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```
### 4. 🔐 Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash

⚠️ A análise por IA depende dessas variáveis.  
Caso não estejam configuradas, o sistema continuará funcionando sem a análise global por IA.

### 5. Rodar aplicação

```bash
python -m streamlit run app/ui/dashboard.py
```

## 🎯 Como usar
1. Execute a aplicação
2. Faça upload de um vídeo
3. Clique em "Analisar vídeo"
4. Visualize os resultados na tela e, se desejar, ative a exibição de marcações na transcrição
    - Transcrição
    - Vícios de linguagem
    - Pausas
    - Repetições

## 📌 Observações
- Projeto em fase de MVP
- A qualidade da transcrição depende do áudio
- Algumas disfluências podem não ser captadas diretamente
- FFmpeg é obrigatório para extração de áudio
- Sem conexão com a internet, a análise por IA é desativada automaticamente
- Dados de entrada (vídeos) não são versionados
- O sistema roda localmente (sem backend remoto)

## 🔮 Próximos passos
- Refinar layout da UI
- Adicionar mais informações a tela de BI
- Melhorar a qualidade e nível de detalhes do relatório (.DOCX editável)
- Aumentar a capacidade de upload de arquivos