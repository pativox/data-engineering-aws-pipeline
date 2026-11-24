-- Cargar el lote en integration.staging_events antes de ejecutar este script.
-- Ejemplo local: usar COPY desde un cliente PostgreSQL con la ruta del CSV curado.
-- La clave primaria de integration.events protege contra reingestas del mismo event_id.

INSERT INTO integration.events
  (event_id, event_type, event_timestamp, customer_id, amount, source)
SELECT DISTINCT ON (event_id)
       event_id, event_type, event_timestamp, customer_id, amount, source
FROM integration.staging_events
WHERE event_id IS NOT NULL
ORDER BY event_id, event_timestamp DESC
ON CONFLICT (event_id) DO NOTHING;

-- Control operacional por tipo de evento y día
SELECT DATE(event_timestamp) AS event_date,
       event_type,
       COUNT(*) AS event_count,
       SUM(amount) AS total_amount
FROM integration.events
GROUP BY 1,2
ORDER BY 1,2;

-- Vaciar staging solo después de validar la carga y guardar métricas del lote.
-- TRUNCATE TABLE integration.staging_events;
