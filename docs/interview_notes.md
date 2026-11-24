# Notas para entrevista — AWS Event Pipeline

## Problema
Procesar eventos de pedidos, pagos y despachos conservando trazabilidad y evitando duplicados.

## Decisiones
- El evento original se conserva en landing para auditoría y reproceso.
- La clave natural `event_id` permite detectar duplicados.
- Los registros inválidos se separan de los válidos y se reportan.
- La carga PostgreSQL usa una restricción única y `ON CONFLICT DO NOTHING`.

## Evolución a AWS
- S3 para landing, curated y rejected.
- Lambda como consumidor de eventos S3.
- IAM con privilegio mínimo.
- CloudWatch para logs, métricas y alarmas.
- DLQ y reintentos con backoff para fallos persistentes.

## Transparencia
La implementación publicada es local. Los servicios AWS son arquitectura objetivo; no se declara despliegue cloud productivo.
