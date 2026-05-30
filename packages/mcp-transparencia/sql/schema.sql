CREATE SCHEMA IF NOT EXISTS transparencia;

CREATE TABLE IF NOT EXISTS transparencia.pages (
    url text PRIMARY KEY,
    canonical text,
    status_code integer,
    breadcrumb text[] NOT NULL DEFAULT '{}',
    title text,
    updated_at date,
    section_count integer NOT NULL DEFAULT 0,
    accordion_count integer NOT NULL DEFAULT 0,
    external_link_count integer NOT NULL DEFAULT 0,
    internal_link_count integer NOT NULL DEFAULT 0,
    crawled_at timestamptz,
    materia_raw text,
    materia_slug text,
    materia_label text,
    search_tsv tsvector NOT NULL DEFAULT ''::tsvector
);

COMMENT ON TABLE transparencia.pages IS 'Paginas rastreadas del Portal de Transparencia en Publicidad Activa.';
COMMENT ON COLUMN transparencia.pages.url IS 'URL canonica usada como identificador estable de la pagina.';
COMMENT ON COLUMN transparencia.pages.breadcrumb IS 'Ruta de navegacion normalizada como array nativo.';
COMMENT ON COLUMN transparencia.pages.materia_slug IS 'Categoria tematica derivada del path o del campo materias; no representa una entidad emisora.';
COMMENT ON COLUMN transparencia.pages.search_tsv IS 'Indice de busqueda textual en castellano construido desde pagina y secciones.';

CREATE TABLE IF NOT EXISTS transparencia.sections (
    id bigserial PRIMARY KEY,
    page_url text NOT NULL REFERENCES transparencia.pages(url) ON DELETE CASCADE,
    ord integer NOT NULL,
    heading text,
    text text,
    content text,
    materia_raw text,
    UNIQUE (page_url, ord)
);

COMMENT ON TABLE transparencia.sections IS 'Bloques de contenido textual extraidos de cada pagina.';
COMMENT ON COLUMN transparencia.sections.ord IS 'Orden estable calculado por pagina durante la carga ETL.';
COMMENT ON COLUMN transparencia.sections.content IS 'Contenido ampliado si el scraper lo proporciona; puede incluir texto antes separado en acordeones.';

CREATE TABLE IF NOT EXISTS transparencia.resource_types (
    id bigserial PRIMARY KEY,
    code text NOT NULL UNIQUE,
    label text NOT NULL,
    description text NOT NULL
);

COMMENT ON TABLE transparencia.resource_types IS 'Tipos entendibles de recurso enlazado para UI y marts.';

CREATE TABLE IF NOT EXISTS transparencia.link_patterns (
    id bigserial PRIMARY KEY,
    name text NOT NULL UNIQUE,
    host_match text,
    path_regex text,
    resource_type_code text NOT NULL REFERENCES transparencia.resource_types(code),
    category text NOT NULL,
    priority integer NOT NULL DEFAULT 0,
    enabled boolean NOT NULL DEFAULT true
);

COMMENT ON TABLE transparencia.link_patterns IS 'Reglas editables de clasificacion de enlaces por host y path.';
COMMENT ON COLUMN transparencia.link_patterns.host_match IS 'Expresion regular aplicada a target_host. NULL equivale a cualquier host.';
COMMENT ON COLUMN transparencia.link_patterns.path_regex IS 'Expresion regular aplicada a target_path o target_url. NULL equivale a cualquier ruta.';

CREATE TABLE IF NOT EXISTS transparencia.links (
    id bigserial PRIMARY KEY,
    source_page_url text NOT NULL REFERENCES transparencia.pages(url) ON DELETE CASCADE,
    ord integer NOT NULL,
    target_url text NOT NULL,
    target_host text,
    target_path text,
    anchor_text text,
    file_extension text,
    scope text NOT NULL DEFAULT 'external',
    is_download boolean NOT NULL DEFAULT false,
    is_noise boolean NOT NULL DEFAULT false,
    materia_raw text,
    pattern_id bigint REFERENCES transparencia.link_patterns(id),
    resource_type_id bigint REFERENCES transparencia.resource_types(id),
    UNIQUE (source_page_url, ord)
);

COMMENT ON TABLE transparencia.links IS 'Hipervinculos normalizados encontrados en las paginas rastreadas.';
COMMENT ON COLUMN transparencia.links.scope IS 'Ambito derivado del enlace: internal, external, download o noise.';
COMMENT ON COLUMN transparencia.links.pattern_id IS 'Regla de mayor prioridad que clasifico el enlace.';
COMMENT ON COLUMN transparencia.links.resource_type_id IS 'Tipo funcional asignado al enlace.';

INSERT INTO transparencia.resource_types (code, label, description) VALUES
    ('internal_page', 'Pagina interna', 'Navegacion interna del Portal de Transparencia.'),
    ('download', 'Documento descargable', 'Recurso descargable como PDF, hoja de calculo o CSV.'),
    ('pap_hacienda', 'PAP Hacienda', 'Enlaces a cuentas, auditorias u otros recursos de la Intervencion General/PAP.'),
    ('boe', 'BOE', 'Normativa o disposiciones oficiales publicadas en boe.es.'),
    ('subvenciones', 'Subvenciones', 'Enlaces al sistema nacional de publicidad de subvenciones.'),
    ('sede', 'Sede electronica', 'Acceso administrativo a la sede electronica del Portal de Transparencia.'),
    ('noise', 'Ruido', 'Anclas, javascript y navegacion irrelevante para busqueda o UI.'),
    ('other', 'Otro', 'Enlace no clasificado por las reglas actuales.')
ON CONFLICT (code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description;

INSERT INTO transparencia.link_patterns (name, host_match, path_regex, resource_type_code, category, priority, enabled) VALUES
    ('ruido javascript', NULL, '^javascript:', 'noise', 'ruido', 1000, true),
    ('ruido ancla', NULL, '^#', 'noise', 'ruido', 990, true),
    ('subvenciones infosubvenciones', '(^|\.)infosubvenciones\.es$', NULL, 'subvenciones', 'subvenciones', 900, true),
    ('subvenciones bdnstrans', NULL, 'bdnstrans', 'subvenciones', 'subvenciones', 890, true),
    ('boe', '(^|\.)boe\.es$', NULL, 'boe', 'normativa', 800, true),
    ('pap hacienda gob', '^www\.pap\.hacienda\.gob\.es$', NULL, 'pap_hacienda', 'cuentas', 790, true),
    ('pap minhafp gob', '^www\.pap\.minhafp\.gob\.es$', NULL, 'pap_hacienda', 'cuentas', 780, true),
    ('sede transparencia', '^transparencia\.sede\.gob\.es$', NULL, 'sede', 'sede', 700, true),
    ('descarga content dam', NULL, '/content/dam/', 'download', 'documento', 650, true),
    ('descarga extension', NULL, '\.(pdf|xls|xlsx|csv|ods)(\?|$)', 'download', 'documento', 640, true),
    ('pagina interna publicidad activa', '(^|\.)transparencia\.gob\.es$', '^/publicidad-activa/', 'internal_page', 'navegacion', 500, true),
    ('otro', NULL, NULL, 'other', 'otro', 0, true)
ON CONFLICT (name) DO UPDATE SET
    host_match = EXCLUDED.host_match,
    path_regex = EXCLUDED.path_regex,
    resource_type_code = EXCLUDED.resource_type_code,
    category = EXCLUDED.category,
    priority = EXCLUDED.priority,
    enabled = EXCLUDED.enabled;

CREATE INDEX IF NOT EXISTS idx_pages_materia_slug ON transparencia.pages(materia_slug);
CREATE INDEX IF NOT EXISTS idx_pages_search_tsv ON transparencia.pages USING gin(search_tsv);
CREATE INDEX IF NOT EXISTS idx_sections_page_ord ON transparencia.sections(page_url, ord);
CREATE INDEX IF NOT EXISTS idx_links_source_ord ON transparencia.links(source_page_url, ord);
CREATE INDEX IF NOT EXISTS idx_links_target_host ON transparencia.links(target_host);
CREATE INDEX IF NOT EXISTS idx_links_resource_type ON transparencia.links(resource_type_id);
CREATE INDEX IF NOT EXISTS idx_links_pattern ON transparencia.links(pattern_id);
CREATE INDEX IF NOT EXISTS idx_link_patterns_priority ON transparencia.link_patterns(priority DESC) WHERE enabled;

CREATE OR REPLACE VIEW transparencia.v_link_categories AS
SELECT
    l.id,
    l.source_page_url,
    l.ord,
    l.target_url,
    l.target_host,
    l.target_path,
    l.anchor_text,
    l.file_extension,
    l.scope,
    l.is_download,
    l.is_noise,
    p.materia_slug,
    p.materia_label,
    COALESCE(rt.code, 'other') AS code,
    COALESCE(rt.label, 'Otro') AS label,
    COALESCE(lp.category, 'otro') AS category,
    lp.name AS pattern_name
FROM transparencia.links l
JOIN transparencia.pages p ON p.url = l.source_page_url
LEFT JOIN transparencia.resource_types rt ON rt.id = l.resource_type_id
LEFT JOIN transparencia.link_patterns lp ON lp.id = l.pattern_id;

CREATE OR REPLACE VIEW transparencia.v_organisms AS
SELECT
    p.materia_slug,
    p.materia_label,
    count(DISTINCT p.url) AS page_count,
    count(l.id) AS link_count,
    count(l.id) FILTER (WHERE vc.code = 'download') AS download_count,
    count(l.id) FILTER (WHERE vc.code = 'boe') AS boe_count,
    count(l.id) FILTER (WHERE vc.code = 'pap_hacienda') AS pap_hacienda_count,
    count(l.id) FILTER (WHERE vc.code = 'subvenciones') AS subvenciones_count
FROM transparencia.pages p
LEFT JOIN transparencia.links l ON l.source_page_url = p.url
LEFT JOIN transparencia.v_link_categories vc ON vc.id = l.id
GROUP BY p.materia_slug, p.materia_label;

COMMENT ON VIEW transparencia.v_organisms IS 'Resumen por materia tematica del portal. El nombre se conserva por compatibilidad; no son organismos emisores.';

CREATE OR REPLACE VIEW transparencia.v_search_pages AS
SELECT
    url,
    title,
    materia_slug,
    materia_label,
    breadcrumb,
    updated_at,
    crawled_at,
    search_tsv
FROM transparencia.pages;
