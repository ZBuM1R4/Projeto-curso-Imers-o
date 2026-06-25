# Banco de dados - Supabase

Esta pasta documenta a estrutura do banco Supabase usado no projeto Análise de Comunicação.

## Arquivos

### `supabase_setup.sql`

Contém a estrutura principal das tabelas, colunas, policies RLS e índices recomendados.

Inclui:

- Tabela `profiles`
- Tabela `analyses`
- Colunas de expiração e status
- Policies de acesso por usuário
- Índices úteis para histórico e consultas por usuário

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