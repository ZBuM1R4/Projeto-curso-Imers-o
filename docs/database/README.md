# Banco de dados - Supabase

Esta pasta documenta a estrutura do banco Supabase usado no projeto Análise de Comunicação.

## Arquivos

### `supabase_setup.sql`

Contém a estrutura principal das tabelas, colunas, policies RLS, índices recomendados e configuração documentada do Supabase Storage.

Inclui:

- Tabela `profiles`
- Tabela `analyses`
- Colunas de expiração e status
- Policies de acesso por usuário
- Índices úteis para histórico e consultas por usuário
- Policies do Supabase Storage para fotos de perfil

### `supabase_checks.sql`

Contém consultas de auditoria para verificar:

- Estrutura das tabelas
- Policies RLS
- Quantidade de análises por status
- Análises sem expiração
- Últimas análises registradas

## Regras atuais do produto

- Cada usuário acessa apenas seus próprios dados.
- Vídeos não são salvos no banco de dados.
- O banco salva apenas relatórios, transcrições, scores e metadados.
- Análises possuem `status`.
- `active`: análise disponível.
- `deleted`: análise descartada pelo usuário.
- O descarte é feito por soft delete.
- Análises descartadas não aparecem no histórico do usuário.
- O limite mensal não é restaurado ao descartar uma análise.
- As análises expiram após 15 dias.

## Tabelas principais

### `profiles`

Armazena os dados cadastrais do usuário.

Campos principais:

- `id`
- `first_name`
- `last_name`
- `cpf`
- `phone`
- `cep`
- `street`
- `number`
- `neighborhood`
- `city`
- `state`
- `avatar_url`
- `created_at`

O campo `avatar_url` armazena a URL pública da foto de perfil salva no Supabase Storage.

### `analyses`

Armazena os dados estruturados das análises realizadas.

Campos principais:

- `id`
- `user_id`
- `title`
- `video_name`
- `score`
- `transcription`
- `report_json`
- `ai_available`
- `created_at`
- `expires_at`
- `status`

A coluna `video_name` guarda apenas o nome/caminho de referência do arquivo usado na análise. O vídeo original não é salvo no banco.

## Supabase Storage

O projeto utiliza Supabase Storage para armazenar fotos de perfil.

Bucket utilizado:

```text
profile-images