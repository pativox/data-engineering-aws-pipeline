-- Patrón de carga idempotente. staging_events representa el lote recibido.
INSERT INTO integration.events
  (event_id, event_type, event_timestamp, customer_id, amount, source)
SELECT event_id, event_type, event_timestamp, customer_id, amount, source
FROM staging_events
ON CONFLICT (event_id) DO NOTHING;

-- Control operacional por tipo de evento y día
SELECT DATE(event_timestamp) AS event_date,
       event_type,
       COUNT(*) AS event_count,
       SUM(amount) AS total_amount
FROM integration.events
GROUP BY 1,2
ORDER BY 1,2;
