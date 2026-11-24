# Runbook — AWS event pipeline

## Requisitos
- Python 3.10 o superior.
- No requiere paquetes externos ni credenciales AWS.

## Ejecución en Windows
Desde PowerShell, en la raíz del repositorio:
```powershell
py -3 src/process_events.py
py -3 -m unittest discover -s tests -p "test_*.py" -v
```

## Ejecución en Linux/macOS
```bash
python3 src/process_events.py
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Salidas
El proceso regenera landing raw, curated, rejected y `reports/run_summary.json`. Estas salidas están excluidas de Git; el archivo de entrada original en `data/incoming/` se mantiene versionado.

## Diagnóstico
- **JSON inválido:** revisar sintaxis y que la raíz sea un arreglo.
- **Eventos rechazados:** consultar `data/rejected/events_rejected.csv` y `reports/run_summary.json`.
- **Duplicados:** `event_id` es la clave de idempotencia del lote.
- **SQL:** ejecutar primero `01_schema.sql`, cargar el CSV curado en `integration.staging_events` y luego ejecutar `02_idempotent_load.sql`.
- **CI:** revisar la pestaña Actions; el workflow ejecuta pipeline y pruebas en push y pull request.

## Reproceso
El proceso local reconstruye todas las salidas desde el JSON de entrada. Para producción distribuida se requerirían control de lote, almacenamiento versionado, DLQ, reintentos, observabilidad y política de retención.
