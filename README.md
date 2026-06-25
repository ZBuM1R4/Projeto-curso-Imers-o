# Análise de Comunicação por Vídeo

Sistema web em Python para análise de comunicação oral a partir de vídeos, com foco em transcrição, avaliação de clareza, fluidez, organização da fala, pausas, repetições, qualidade comunicativa e geração de relatório em DOCX.

O projeto foi desenvolvido como MVP para apoiar avaliações pedagógicas de comunicação, permitindo que usuários enviem vídeos de fala/apresentação e recebam um feedback estruturado com apoio de inteligência artificial.

---

## Funcionalidades principais

* Cadastro e login de usuários com Supabase Auth.
* Cadastro e edição de perfil do usuário.
* Upload de vídeo pela interface web.
* Pré-visualização do vídeo antes da análise.
* Extração automática de áudio com FFmpeg.
* Transcrição automática com Whisper.
* Análise de pausas e tempo de silêncio.
* Identificação de repetições sequenciais e termos recorrentes.
* Avaliação global da comunicação com Gemini.
* Cálculo de score de comunicação.
* Histórico de análises por usuário.
* Limite mensal de análises.
* Expiração automática das análises após 15 dias.
* Descarte de análise com confirmação.
* Geração de relatório profissional em DOCX.
* Interface web com Streamlit.

---

## Critérios de avaliação

O sistema avalia a comunicação considerando:

* Controle de linguagem.
* Clareza.
* Formalidade.
* Fluidez.
* Qualidade geral da comunicação.
* Pausas longas.
* Repetições.
* Termos recorrentes.
* Organização e objetividade da fala.

Observação: vícios de linguagem e muletas de fala podem impactar o score internamente, mas não são exibidos como seção específica nos detalhes da análise ou no relatório DOCX.

---

## Tecnologias utilizadas

* Python
* Streamlit
* Supabase Auth
* Supabase Database
* OpenAI Whisper
* Google Gemini API
* FFmpeg
* python-docx
* Matplotlib
* Git/GitHub

---

## Requisitos

* Python 3.10 ou superior.
* FFmpeg instalado e configurado no PATH.
* Conta/projeto no Supabase.
* Chave da Gemini API.
* Ambiente virtual Python.

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as variáveis necessárias.

Exemplo:

```env
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase

GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-2.5-flash
```

A análise depende da conexão com a internet, do Supabase e da Gemini API.

---

## Estrutura atual do projeto

```text
app/
├── database/
│   ├── profile_db.py
│   └── supabase_db.py
│
├── services/
│   ├── analysis_pipeline.py
│   ├── attention_points_analyzer.py
│   ├── audio_extractor.py
│   ├── docx_exporter.py
│   ├── gemini_full_context_analyzer.py
│   ├── network_checker.py
│   ├── pause_analyzer.py
│   ├── repetition_analyzer.py
│   ├── report_builder.py
│   ├── score_analyzer.py
│   ├── supabase_client.py
│   ├── temp_file_cleaner.py
│   └── transcriber.py
│
├── ui/
│   ├── components/
│   │   ├── avatar.py
│   │   ├── navigation.py
│   │   ├── report_view.py
│   │   ├── score.py
│   │   └── sidebar.py
│   │
│   ├── pages/
│   │   ├── analysis.py
│   │   ├── auth.py
│   │   ├── detail.py
│   │   ├── history.py
│   │   ├── home.py
│   │   └── profile.py
│   │
│   ├── dashboard.py
│   ├── session_state.py
│   └── styles.py
│
├── utils/
│   ├── file_manager.py
│   └── validators.py
│
└── main.py

data/
├── input/
├── temp/
├── output/
└── profile_images/
```

---

## Entrada principal da aplicação

O arquivo principal do projeto é:

```text
app/main.py
```

Ele chama o roteador principal da interface:

```text
app/ui/dashboard.py
```

O `dashboard.py` centraliza a navegação entre páginas, aplicação de estilos, autenticação de sessão e verificação de perfil.

---

## Como rodar o projeto

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual no Git Bash

```bash
source .venv/Scripts/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar a aplicação

```bash
python -m streamlit run app/main.py
```

### 5. Parar o Streamlit

```bash
Ctrl + C
```

---

## Fluxo de uso

1. Usuário acessa a aplicação.
2. Faz login ou cria uma conta.
3. Completa o cadastro de perfil, caso ainda não tenha feito.
4. Acessa a página inicial.
5. Envia um vídeo na tela de análise.
6. Confere a pré-visualização do vídeo.
7. Inicia a análise.
8. O sistema extrai o áudio, transcreve, avalia a comunicação e salva o relatório.
9. O usuário visualiza o resultado na tela.
10. O usuário pode baixar o relatório em DOCX.
11. O usuário pode acompanhar análises anteriores no histórico.

---

## Regras de armazenamento e privacidade

* Os vídeos enviados não são armazenados no banco de dados.
* Os vídeos são salvos apenas temporariamente durante o uso da aplicação.
* Os arquivos temporários ficam em `data/input/` e `data/temp/`.
* O sistema limpa os arquivos temporários em momentos importantes do fluxo, como login, logout, nova análise e troca de análise.
* O banco salva apenas os dados da análise e o relatório estruturado.
* Fotos de perfil ficam em `data/profile_images/`.
* As pastas de dados são preservadas no Git com arquivos `.gitkeep`.

---

## Limite mensal e expiração

* Cada usuário possui limite mensal de análises.
* O limite atual é de 30 análises por mês.
* As análises ficam disponíveis no histórico por 15 dias.
* Após o prazo, deixam de aparecer para o usuário.
* Ao descartar uma análise, ela sai do histórico do usuário, mas o limite mensal utilizado não é restaurado.
* O descarte é feito por soft delete, preservando o registro no banco para fins de controle e acompanhamento.

---

## Banco de dados

O projeto utiliza Supabase para autenticação e persistência de dados.

Principais tabelas:

```text
profiles
analyses
```

A tabela `profiles` armazena os dados cadastrais do usuário.

A tabela `analyses` armazena os dados estruturados das análises, incluindo:

```text
user_id
title
video_name
score
transcription
report_json
ai_available
created_at
expires_at
status
```

As políticas de RLS devem garantir que cada usuário acesse apenas seus próprios dados.

---

## Relatório DOCX

O sistema gera um relatório editável em DOCX contendo:

* Score geral.
* Classificação.
* Resumo da análise.
* Transcrição.
* Pontos de atenção.
* Pausas.
* Repetições.
* Análise global por IA.
* Recomendações e observações.

---

## Comandos úteis

Rodar aplicação:

```bash
python -m streamlit run app/main.py
```

Atualizar dependências:

```bash
pip freeze > requirements.txt
```

Limpar arquivos temporários manualmente:

```bash
find data/input data/temp -type f ! -name ".gitkeep" -delete
```

Verificar erros de compilação:

```bash
python -m compileall app
```

Ver status do Git:

```bash
git status
```

Commit padrão:

```bash
git add .
git commit -m "Mensagem do commit"
git push origin main
```

---

## Status do projeto

Projeto em fase de MVP funcional, com autenticação, análise de vídeo, histórico, relatórios, controle mensal, expiração de análises e interface modularizada.

---

## Próximas etapas

* Revisar documentação final do projeto.
* Revisar mensagens e textos da interface.
* Preparar checklist de deploy.
* Otimizar custos e uso de tokens da IA.
* Avaliar painel administrativo.
* Avaliar regras futuras para usuários admin/dev.
* Melhorar monitoramento e logs.
* Preparar deploy web.
