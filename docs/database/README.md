# Banco de dados - Supabase

Esta pasta documenta a estrutura do banco Supabase usado no projeto Análise de Comunicação.

## Arquivos

### `supabase_setup.sql`

Contém a estrutura principal das tabelas, colunas, policies RLS, índices recomendados e configuração documentada do Supabase Storage.

Inclui:

* Tabela `profiles`
* Tabela `analyses`
* Colunas de expiração, status e tipo de entrada da análise
* Policies de acesso por usuário
* Índices úteis para histórico e consultas por usuário
* Policies do Supabase Storage para fotos de perfil

### `supabase_checks.sql`

Contém consultas de auditoria para verificar:

* Estrutura das tabelas
* Policies RLS
* Quantidade de análises por status
* Análises sem expiração
* Últimas análises registradas

## Regras atuais do produto

* Cada usuário acessa apenas seus próprios dados.
* Vídeos não são salvos no banco de dados.
* Áudios gravados na versão web não são salvos no banco de dados.
* O banco salva apenas relatórios, transcrições, scores e metadados.
* Análises possuem `status`.
* `active`: análise disponível.
* `deleted`: análise descartada pelo usuário.
* O descarte é feito por soft delete.
* Análises descartadas não aparecem no histórico do usuário.
* O limite mensal não é restaurado ao descartar uma análise.
* As análises expiram após 15 dias.
* Cada análise possui um `input_type`, indicando se foi feita por áudio ou vídeo.

## Tabelas principais

### `profiles`

Armazena os dados cadastrais do usuário.

Campos principais:

* `id`
* `first_name`
* `last_name`
* `cpf`
* `phone`
* `cep`
* `street`
* `number`
* `neighborhood`
* `city`
* `state`
* `avatar_url`
* `created_at`

O campo `avatar_url` armazena a URL pública da foto de perfil salva no Supabase Storage.

### `analyses`

Armazena os dados estruturados das análises realizadas.

Campos principais:

* `id`
* `user_id`
* `title`
* `video_name`
* `input_type`
* `score`
* `transcription`
* `report_json`
* `ai_available`
* `created_at`
* `expires_at`
* `status`

A coluna `video_name` guarda apenas uma referência textual ao insumo usado na análise. Em análises por vídeo, pode indicar o nome/caminho temporário do arquivo utilizado. Em análises por áudio gravado na versão web, o valor salvo deve ser `audio_recording`.

O conteúdo bruto original, seja áudio ou vídeo, não é salvo no banco de dados.

O campo `input_type` identifica a origem da análise:

* `audio`: análise feita a partir de áudio gravado na versão web.
* `video`: análise feita a partir de vídeo enviado na versão local.

## Supabase Storage

O projeto utiliza Supabase Storage para armazenar fotos de perfil.

Bucket utilizado:

```text
profile-images
```

Regras:

* O bucket é público para permitir carregamento da imagem pela URL pública.
* A policy pública ampla de listagem foi removida.
* Cada usuário autenticado só pode visualizar, gravar, atualizar ou remover arquivos dentro da própria pasta.
* O caminho padrão da imagem é `{user_id}/avatar`.
* A URL pública da imagem é salva no campo `profiles.avatar_url`.
* Vídeos de análise não são enviados para o Storage.
* Áudios gravados na versão web não são enviados para o Storage.
* Vídeos e áudios continuam sendo usados apenas como arquivos temporários durante a sessão/análise.

## Policies RLS

As policies seguem a regra de propriedade por usuário.

### `profiles`

* Usuário pode visualizar apenas o próprio perfil.
* Usuário pode criar apenas o próprio perfil.
* Usuário pode atualizar apenas o próprio perfil.

### `analyses`

* Usuário pode visualizar apenas as próprias análises.
* Usuário pode criar apenas análises vinculadas ao próprio usuário.
* Usuário pode atualizar apenas as próprias análises.
* Usuário pode deletar apenas as próprias análises.

Observação: atualmente o app utiliza soft delete para descarte de análises, atualizando o campo `status` para `deleted`.

## Expiração de análises

As análises possuem a coluna:

```text
expires_at
```

A regra atual é:

```text
created_at + 15 dias
```

O histórico do usuário exibe apenas análises com:

```text
status = active
expires_at > data atual
```

## Limite mensal

O limite mensal atual é de 30 análises por usuário.

O descarte de uma análise não restaura o limite mensal, pois o relatório continua registrado no banco para controle e acompanhamento pedagógico.

## Privacidade e armazenamento

* Vídeos não são salvos no banco.
* Vídeos não são enviados ao Supabase Storage.
* Vídeos ficam apenas temporariamente em `data/input/`.
* Áudios gravados na versão web são usados apenas temporariamente para transcrição e análise.
* Áudios brutos não são salvos no banco de dados.
* Áudios brutos não são enviados ao Supabase Storage.
* Áudios temporários ficam em `data/temp/` apenas durante o processamento.
* Fotos de perfil são salvas no Supabase Storage.
* Relatórios, transcrições, scores e metadados são salvos no banco.
* O campo `input_type` registra se a análise foi feita por `audio` ou `video`.

## Observações para deploy

Antes do deploy, verificar:

* Variáveis de ambiente do Supabase.
* Variáveis de ambiente da Gemini API.
* Valor correto de `APP_MODE`.
* Bucket `profile-images` criado no Supabase Storage.
* Policies do Storage aplicadas corretamente.
* FFmpeg disponível no ambiente de hospedagem quando o modo local/vídeo for utilizado.
* Pastas temporárias disponíveis para processamento local.
* Fluxo web por áudio funcionando sem persistir o áudio bruto.