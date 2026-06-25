-- Consultas úteis para auditoria do banco Supabase

-- Estrutura das tabelas principais
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('profiles', 'analyses')
ORDER BY table_name, ordinal_position;


-- Policies RLS
SELECT
    schemaname,
    tablename,
    policyname,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('profiles', 'analyses')
ORDER BY tablename, policyname;


-- Quantidade de análises por status
SELECT
    status,
    COUNT(*) AS total
FROM public.analyses
GROUP BY status
ORDER BY status;


-- Análises sem data de expiração
SELECT
    COUNT(*) AS analyses_without_expiration
FROM public.analyses
WHERE expires_at IS NULL;


-- Últimas análises registradas
SELECT
    id,
    title,
    video_name,
    score,
    created_at,
    expires_at,
    status
FROM public.analyses
ORDER BY created_at DESC
LIMIT 10;