# Proyecto 2 — Integración de eventos empresariales (AWS)

## Resumen ejecutivo
Pipeline batch de eventos JSON que implementa almacenamiento raw, validación, deduplicación y publicación de una capa curada. El diseño representa un patrón serverless basado en S3 + Lambda; la ejecución incluida es local.

**Stack:** Python 3.10+, JSON, SQL y PostgreSQL (SQL de referencia).  
**Ejecución local:** Python estándar, sin dependencias externas ni recursos AWS.

## Caso de negocio
Una compañía recibe eventos de pedidos, pagos y despachos desde una API de comercio. Requiere trazabilidad, procesamiento reproducible y una capa curada para reportería operacional.

## Arquitectura lógica
- **Landing/raw:** conserva el payload JSON recibido.
- **Validación:** verifica estructura, campos obligatorios, timestamp, monto finito/no negativo y cliente informado.
- **Deduplicación:** usa `event_id` como clave natural.
- **Curated/rejected:** separa eventos válidos de registros rechazados con motivo y número de fila.
- **Persistencia opcional:** SQL PostgreSQL con restricción única y patrón `ON CONFLICT DO NOTHING`.

## Ejecución local
Desde la raíz del repositorio:
```bash
python src/process_events.py
python -m unittest discover -s tests -p "test_*.py" -v
```

Produce:
- `data/landing/events_raw.json`
- `data/curated/events_curated.csv`
- `data/rejected/events_rejected.csv`
- `reports/run_summary.json`

## Controles de calidad
- El payload raíz debe ser un arreglo JSON.
- Cada elemento debe ser un objeto.
- Campos obligatorios presentes; identificador, tipo, origen y cliente no vacíos.
- `event_id` único dentro del lote.
- Timestamp ISO válido.
- Importe numérico, finito y no negativo.
- Salidas con encabezados estables incluso cuando no existan registros aceptados/rechazados.
- Reporte de cantidades y motivos de rechazo.

## Idempotencia y reproceso
El procesamiento local reconstruye las salidas desde el JSON raw, por lo que una nueva ejecución no acumula duplicados en los archivos. Para persistencia relacional, `sql/postgresql/02_idempotent_load.sql` usa `ON CONFLICT (event_id) DO NOTHING`. En una solución distribuida se debe complementar con identificador de lote/checkpoint y política de reintentos.

## SQL / PostgreSQL
Los scripts de `sql/postgresql/` crean la tabla final y una tabla staging para recibir el lote curado. La carga final aplica `DISTINCT ON (event_id)` y `ON CONFLICT DO NOTHING`. La conexión a PostgreSQL no forma parte de la ejecución local.

## Calidad continua
GitHub Actions ejecuta el pipeline y las pruebas unitarias en cada push y pull request. El resultado real se consulta en la pestaña **Actions**.

## Evolución AWS (diseño, no despliegue)
1. API Gateway recibe eventos autenticados.
2. S3 almacena el objeto raw con versionado y cifrado.
3. Lambda valida y transforma el evento o lote.
4. S3 separa curated y rejected.
5. SQS DLQ gestiona fallos persistentes; reintentos con backoff.
6. IAM aplica mínimo privilegio y CloudWatch centraliza logs, métricas y alarmas.
7. RDS PostgreSQL puede servir como destino relacional cuando el caso de uso lo requiera.

No se ha desplegado infraestructura AWS en este repositorio. El proyecto es demostrable sin cuenta cloud ni costos.

## Documentación complementaria
- [Diagrama de arquitectura](docs/architecture.md)
- [Runbook de ejecución y carga SQL](docs/runbook.md)

Los archivos generados en landing, curated, rejected y reports se excluyen de Git mediante `.gitignore`.

## Decisiones técnicas para entrevista
- Raw conserva evidencia para auditoría y reproceso.
- Validación previa evita contaminar la capa curada.
- La clave natural evita duplicidad dentro del lote.
- Decimal evita errores de punto flotante en importes.
- La separación curated/rejected permite monitorear calidad sin perder trazabilidad.
- Las pruebas unitarias cubren reglas de negocio y entradas malformadas.
