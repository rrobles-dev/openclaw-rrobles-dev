# Notas de configuración

- Telegram: bot creado con BotFather; token cargado con `read -s` para no dejarlo en el historial de bash. Acceso restringido con pairing (lista blanca por user id).
- Zapier MCP: agregado con `openclaw mcp add` (transporte streamable-http, auth OAuth) en vez del flujo con mcporter, para no instalar dependencias extra en un VPS de 1 GB de RAM.
- OAuth en servidor sin navegador: el callback a 127.0.0.1 fallaba desde el navegador local; se resolvió con `openclaw mcp login zapier --code <code>`.
- Problema: una auto-actualización de OpenClaw (2026.9.7 → 2026.9.8) detuvo el gateway y no lo reinició; se diagnosticó con `systemctl --user status` y se levantó manualmente.
- Zona horaria: el VPS corre en UTC, así que se indicó fecha exacta y America/Santiago al agendar.
- Hallazgo de seguridad: aunque en Zapier se habilitaron solo 2 acciones, el conector expone 17 tools (incluye borrar eventos). Se usó una cuenta Google de prueba para limitar el impacto.