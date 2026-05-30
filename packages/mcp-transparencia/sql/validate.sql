\echo '== Transparencia validation =='
\echo ''

\echo '1. Expected tables and views'
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'transparencia'
ORDER BY table_type, table_name;

\echo ''
\echo '2. Base counts'
SELECT 'pages' AS relation, count(*) AS rows FROM transparencia.pages
UNION ALL
SELECT 'sections', count(*) FROM transparencia.sections
UNION ALL
SELECT 'accordion', count(*) FROM transparencia.accordion
UNION ALL
SELECT 'links', count(*) FROM transparencia.links
UNION ALL
SELECT 'resource_types', count(*) FROM transparencia.resource_types
UNION ALL
SELECT 'link_patterns', count(*) FROM transparencia.link_patterns
ORDER BY relation;

\echo ''
\echo '3. Critical nulls: expected 0 in every row'
SELECT 'pages.url' AS check_name, count(*) AS failures
FROM transparencia.pages
WHERE url IS NULL OR url = ''
UNION ALL
SELECT 'sections.page_url', count(*)
FROM transparencia.sections
WHERE page_url IS NULL OR page_url = ''
UNION ALL
SELECT 'accordion.page_url', count(*)
FROM transparencia.accordion
WHERE page_url IS NULL OR page_url = ''
UNION ALL
SELECT 'links.source_page_url', count(*)
FROM transparencia.links
WHERE source_page_url IS NULL OR source_page_url = ''
UNION ALL
SELECT 'links.target_url', count(*)
FROM transparencia.links
WHERE target_url IS NULL OR target_url = ''
ORDER BY check_name;

\echo ''
\echo '4. Referential integrity: expected 0 in every row'
SELECT 'orphan sections' AS check_name, count(*) AS failures
FROM transparencia.sections s
LEFT JOIN transparencia.pages p ON p.url = s.page_url
WHERE p.url IS NULL
UNION ALL
SELECT 'orphan accordion', count(*)
FROM transparencia.accordion a
LEFT JOIN transparencia.pages p ON p.url = a.page_url
WHERE p.url IS NULL
UNION ALL
SELECT 'orphan links', count(*)
FROM transparencia.links l
LEFT JOIN transparencia.pages p ON p.url = l.source_page_url
WHERE p.url IS NULL;

\echo ''
\echo '5. Duplicated ord per page: expected 0 rows'
SELECT 'sections' AS relation, page_url AS url, ord, count(*) AS rows
FROM transparencia.sections
GROUP BY page_url, ord
HAVING count(*) > 1
UNION ALL
SELECT 'accordion', page_url, ord, count(*)
FROM transparencia.accordion
GROUP BY page_url, ord
HAVING count(*) > 1
UNION ALL
SELECT 'links', source_page_url, ord, count(*)
FROM transparencia.links
GROUP BY source_page_url, ord
HAVING count(*) > 1
ORDER BY relation, url, ord
LIMIT 50;

\echo ''
\echo '6. Materia distribution'
SELECT materia_slug, materia_label, count(*) AS pages
FROM transparencia.pages
GROUP BY materia_slug, materia_label
ORDER BY pages DESC, materia_slug;

\echo ''
\echo '7. Materia outliers to review'
SELECT materia_slug, url
FROM transparencia.pages
WHERE materia_slug IS NULL
   OR materia_slug IN ('paley', 'por-materias')
ORDER BY materia_slug NULLS LAST, url;

\echo ''
\echo '8. Link classification completeness: expected 0'
SELECT count(*) AS unclassified_links
FROM transparencia.links
WHERE resource_type_id IS NULL OR pattern_id IS NULL;

\echo ''
\echo '9. Link category distribution'
SELECT code, category, count(*) AS links
FROM transparencia.v_link_categories
GROUP BY code, category
ORDER BY links DESC, code, category;

\echo ''
\echo '10. Other links by host'
SELECT target_host, count(*) AS links
FROM transparencia.v_link_categories
WHERE code = 'other'
GROUP BY target_host
ORDER BY links DESC, target_host
LIMIT 30;

\echo ''
\echo '11. Download extensions'
SELECT file_extension, count(*) AS links
FROM transparencia.links
WHERE is_download
GROUP BY file_extension
ORDER BY links DESC, file_extension;

\echo ''
\echo '12. Search vector coverage'
SELECT count(*) AS empty_search_tsv
FROM transparencia.pages
WHERE search_tsv = ''::tsvector;

\echo ''
\echo '13. Search samples: empleo'
SELECT title, materia_slug, url
FROM transparencia.v_search_pages
WHERE search_tsv @@ plainto_tsquery('spanish', 'empleo')
LIMIT 10;

\echo ''
\echo '14. Search samples: contratos'
SELECT title, materia_slug, url
FROM transparencia.v_search_pages
WHERE search_tsv @@ plainto_tsquery('spanish', 'contratos')
LIMIT 10;

\echo ''
\echo '15. View count consistency: expected same left and right'
SELECT 'v_link_categories vs links' AS check_name,
       (SELECT count(*) FROM transparencia.v_link_categories) AS view_rows,
       (SELECT count(*) FROM transparencia.links) AS table_rows
UNION ALL
SELECT 'v_search_pages vs pages',
       (SELECT count(*) FROM transparencia.v_search_pages),
       (SELECT count(*) FROM transparencia.pages);

\echo ''
\echo '16. Duplicate page URLs after normalization: expected 0 rows'
SELECT lower(trim(url)) AS normalized_url, count(*) AS rows
FROM transparencia.pages
GROUP BY lower(trim(url))
HAVING count(*) > 1
ORDER BY rows DESC, normalized_url
LIMIT 50;

\echo ''
\echo '17. Repeated links by page and target'
SELECT source_page_url, target_url, count(*) AS rows
FROM transparencia.links
GROUP BY source_page_url, target_url
HAVING count(*) > 1
ORDER BY rows DESC, source_page_url, target_url
LIMIT 50;

\echo ''
\echo '18. Text quality checks'
SELECT 'pages without title' AS check_name, count(*) AS rows
FROM transparencia.pages
WHERE title IS NULL OR title = ''
UNION ALL
SELECT 'empty sections', count(*)
FROM transparencia.sections
WHERE coalesce(heading, '') = ''
  AND coalesce(text, '') = ''
  AND coalesce(content, '') = ''
UNION ALL
SELECT 'empty accordion', count(*)
FROM transparencia.accordion
WHERE coalesce(title, '') = ''
  AND coalesce(content, '') = ''
UNION ALL
SELECT 'links without anchor_text', count(*)
FROM transparencia.links
WHERE anchor_text IS NULL OR anchor_text = ''
ORDER BY check_name;

\echo ''
\echo '19. BOE samples'
SELECT target_host, target_url, anchor_text
FROM transparencia.v_link_categories
WHERE code = 'boe'
ORDER BY target_host, target_url
LIMIT 10;

\echo ''
\echo '20. PAP Hacienda samples'
SELECT target_host, target_url, anchor_text
FROM transparencia.v_link_categories
WHERE code = 'pap_hacienda'
ORDER BY target_host, target_url
LIMIT 10;

\echo ''
\echo '21. Subvenciones samples'
SELECT target_host, target_url, anchor_text
FROM transparencia.v_link_categories
WHERE code = 'subvenciones'
ORDER BY target_host, target_url
LIMIT 10;

\echo ''
\echo '22. Basic query plans'
EXPLAIN ANALYZE
SELECT title, url
FROM transparencia.v_search_pages
WHERE search_tsv @@ plainto_tsquery('spanish', 'empleo')
LIMIT 20;

EXPLAIN ANALYZE
SELECT *
FROM transparencia.v_link_categories
WHERE code = 'boe'
LIMIT 100;

\echo ''
\echo '== Validation finished =='
