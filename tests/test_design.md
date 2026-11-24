# Estrategia de pruebas

La validación continua ejecuta el pipeline con Python 3.11 mediante GitHub Actions.

Casos a automatizar con pytest:
- Evento válido se publica en curated.
- `event_id` duplicado se rechaza.
- Timestamp inválido se rechaza.
- Monto negativo se rechaza.
- Reejecución desde el mismo origen produce el mismo conjunto de claves.
