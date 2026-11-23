# Scripts de pruebas automatizadas de extremo a extremo

Dos scripts que prueban HayPaComer desde fuera, como lo usaría una persona: uno por la API REST y otro con un navegador real. Complementan a las pruebas de JUnit del backend (ver [`../pruebas-automatizadas.md`](../pruebas-automatizadas.md)).

| Script | Qué prueba | Cómo | Resultado del 21/11/2026 |
| --- | --- | --- | --- |
| [`smoke_api.py`](smoke_api.py) | Las rutas de la API: cuentas, casas, código para unirse, nevera, inventario, permisos y notificaciones, mercado, recetas, plan semanal, cocina, dispositivos e IA | Python estándar (`urllib`), con 3 cuentas temporales | **147 / 147 OK** ([salida](../resultados/resultado-smoke.txt)) |
| [`e2e_ui.py`](e2e_ui.py) | La interfaz en Chromium con dos personas: registro, crear casa, nevera, agregar 2 latas por unidades, código, unirse, pedir permiso, notificación, aprobar, pestañas, cambio de tamaño de pantalla y cerrar sesión | Playwright | **29 / 32 OK**: encontró 2 defectos reales ([salida](../resultados/resultado-e2e.txt)) |

## Cómo correrlos

Con el backend corriendo en local (`http://localhost:8090`; ver el runbook):

```bash
# 1. API: no necesita nada aparte de Python 3
python3 -I sprint-4/scripts/smoke_api.py                 # o: python3 -I sprint-4/scripts/smoke_api.py https://otra-url

# 2. Navegador: necesita Playwright (pip install playwright && playwright install chromium)
python3 sprint-4/scripts/e2e_ui.py "$(which chromium)" sprint-4/img   # chrome a usar y carpeta para las capturas
```

Cada línea dice `OK` o `FAIL` con lo esperado y lo obtenido; al final imprime el total. Los scripts crean cuentas `tmp-*@local.test` y `e2e-*@local.test`, y borran las casas que crean, pero no hay endpoint para borrar usuarios. Después de correrlos, en una base de pruebas:

```sql
DELETE FROM users WHERE email LIKE 'tmp-%@local.test' OR email LIKE 'e2e-%@local.test';
```

## Qué verifica `smoke_api.py`, además de los códigos HTTP

- Una persona solo puede estar en una casa: crear o unirse estando en otra responde 409.
- El código acepta minúsculas, y un código falso responde 400.
- Quien no creó la casa no puede sacar a nadie ni eliminarla (403), pero sí renombrarla, montar la nevera o conectar sensores.
- Al guardar 2 latas por unidades, el inventario devuelve `pieceGrams = 360` y 720 g; tras consumir una queda 1.
- La comida "preguntar antes" no se puede consumir sin permiso (403). Pedir permiso dos veces es la misma solicitud. Nadie aprueba su propia solicitud, y responder dos veces da 409.
- La notificación de la solicitud le llega **solo** a quien guardó la comida, y la de la respuesta solo a quien pidió.
- La IA (Gemini) aprende un alimento nuevo y el chef responde.
