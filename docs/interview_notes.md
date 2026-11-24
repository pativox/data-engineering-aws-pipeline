# Guía de defensa técnica — Proyecto AWS

## Pitch de 60 segundos
Implementé una solución de integración orientada a eventos. El archivo JSON representa la respuesta de una API y el landing simula S3. Un proceso equivalente a Lambda valida esquema, fecha y monto, aplica deduplicación por `event_id` y separa eventos válidos de rechazados. El modelo PostgreSQL aplica clave primaria, restricciones e índices para consultas operacionales.

## Preguntas de entrevista
1. ¿Cómo aseguras idempotencia? Clave única de evento y `ON CONFLICT DO NOTHING`; en escenarios complejos, ledger/checkpoint por lote.
2. ¿Qué pasa si Lambda falla? Reintentos, DLQ, logs correlacionados y reproceso desde landing.
3. ¿Cómo controlas costos? Procesamiento por evento/lote, límites de concurrencia, lifecycle S3, retención de logs y dimensionamiento de RDS.
4. ¿Cómo proteges datos? IAM mínimo privilegio, cifrado, secretos administrados y datos sensibles minimizados.
5. ¿Cómo escalas? SQS entre ingesta y procesamiento, Lambda concurrency, particionamiento y procesamiento por lotes.
6. ¿Qué monitoreas? Eventos recibidos, válidos, rechazados, latencia, errores y antigüedad del último evento.

## Evolución
- API Gateway para exponer endpoint.
- SQS para desacoplar productores y consumidores.
- DLQ para fallos persistentes.
- Glue/Athena para analítica sobre S3 si corresponde.
- CI/CD con GitHub Actions y pruebas automatizadas.
