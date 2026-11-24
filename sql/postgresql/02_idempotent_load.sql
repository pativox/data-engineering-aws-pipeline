-- staging_events representa el lote validado recibido.
INSERT INTO integration.events (event_id,event_type,event_timestamp,customer_id,amount,source)
SELECT event_id,event_type,event_timestamp,customer_id,amount,source FROM staging_events
ON CONFLICT (event_id) DO NOTHING;
