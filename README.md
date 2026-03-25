# Análise de Comunicação por Vídeo

Projeto em Python para análise de comunicação a partir de vídeos, com foco em identificação de padrões como pausas, vícios de linguagem e repetição de termos.

## 🚀 Funcionalidades (MVP)

- Upload de vídeo via interface web
- Pré-visualização do vídeo
- Transcrição automática (Whisper)
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

## 📂 Estrutura do projeto

```
├── app/
│   ├── ui/
│   │   └── dashboard.py
│   └── services/
├── data/
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

### 4. Rodar aplicação

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
- O sistema roda localmente (sem backend remoto)

## 🔮 Próximos passos
- Melhorar análise semântica da transcrição
- Adicionar gráficos (barras e pizza)
- Refinar detecção de vícios
- Exportação de relatórios