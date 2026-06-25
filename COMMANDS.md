# COMMANDS.md

## 🚀 Comando principal do Streamlit

Rodar o aplicativo:

```bash
python -m streamlit run app/main.py
```

Parar o aplicativo:

```bash
Ctrl + C
```

---

## 🔧 Ambiente virtual

Criar ambiente virtual, se precisar:

```bash
python -m venv .venv
```

Ativar ambiente virtual no Git Bash:

```bash
source .venv/Scripts/activate
```

---

## 📦 Instalação e dependências

Instalar dependências do projeto:

```bash
pip install -r requirements.txt
```

Instalar uma biblioteca específica:

```bash
pip install nome-da-lib
```

Atualizar o `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## ▶️ Execução

Rodar interface principal:

```bash
python -m streamlit run app/main.py
```

Debug rápido de importação/estrutura:

```bash
python app/main.py
```

Observação: o comando acima não substitui o Streamlit. Ele serve apenas para verificar erros simples de Python/importação.

---

## 🧪 Testes e validações rápidas

Verificar erros de compilação/importação:

```bash
python -m compileall app
```

Rodar o app para teste manual:

```bash
python -m streamlit run app/main.py
```

Fluxo básico para testar antes de commit:

```text
Login
Home
Análise
Histórico
Detalhe da análise
Perfil
Logout
```

---

## 🔎 Buscas úteis no projeto

Procurar uma função ou termo no código:

```bash
grep -R "termo_procurado" app
```

Exemplos:

```bash
grep -R "render_analysis" app
grep -R "generate_report" app
grep -R "vicios_de_linguagem" app
```

Buscar ignorando caches:

```bash
grep -R "termo_procurado" app --exclude-dir=__pycache__
```

---

## 🧹 Limpeza de arquivos temporários

Limpar vídeos e áudios temporários manualmente:

```bash
find data/input data/temp -type f ! -name ".gitkeep" -delete
```

Limpar caches Python:

```bash
find app -type d -name "__pycache__" -exec rm -rf {} +
```

Observação: não limpar `data/profile_images/` com esse comando, pois essa pasta guarda fotos de perfil.

---

## 🧾 Git — versionamento

Ver status:

```bash
git status
```

Adicionar mudanças:

```bash
git add .
```

Fazer commit:

```bash
git commit -m "Mensagem do commit"
```

Enviar para o repositório remoto:

```bash
git push origin main
```

Fluxo completo mais usado:

```bash
git status
git add .
git commit -m "Mensagem do commit"
git push origin main
```

---

## ✅ Fluxo recomendado antes de commit

Rodar validação:

```bash
python -m compileall app
```

Rodar o app:

```bash
python -m streamlit run app/main.py
```

Testar rapidamente:

```text
Login
Home
Análise
Histórico
Detalhe
Perfil
Logout
```

Depois commitar:

```bash
git status
git add .
git commit -m "Mensagem do commit"
git push origin main
```

---

## 🌱 Branches

Criar nova branch:

```bash
git checkout -b nome-da-branch
```

Voltar para a branch main:

```bash
git checkout main
```

Mesclar branch na branch atual:

```bash
git merge nome-da-branch
```

---

## 📁 Pastas importantes

```text
app/main.py                  Entrada oficial do Streamlit
app/ui/dashboard.py          Roteador interno da interface
app/ui/pages/                Páginas do sistema
app/ui/components/           Componentes reutilizáveis
app/services/                Serviços e lógica de análise
app/database/                Integração com Supabase
app/utils/                   Utilitários
data/input/                  Vídeos temporários
data/temp/                   Áudios temporários
data/output/                 Saídas geradas, se necessário
data/profile_images/         Fotos de perfil
```