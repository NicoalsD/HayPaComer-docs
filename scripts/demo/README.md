# Scripts de la demo (v1.2.0)

`seed.py` prepara el hogar de la demo y `sensors.py` simula el ESP32. Vienen del monorepo [Juansit-0/HayPaComer](https://github.com/Juansit-0/HayPaComer/tree/main/scripts/demo) (v1.1.0) y aquí están ajustados para la v1.2.0. Solo usan la librería estándar de Python 3.

## Qué se cambió

En la v1.2.0 los enlaces de invitación tienen la forma `/#/join?token=...` y en la v1.1.0 eran `/#token=...`. Con el patrón viejo, `seed.py` no encontraba la invitación de Ana en el log y Ana quedaba sin unirse al hogar. El patrón nuevo acepta las dos formas y solo toma enlaces de invitación.

## Cómo se usan

Con la app corriendo con `MAIL_LOG_LINKS=true` y su log guardado en un archivo (por ejemplo `demo.log`):

```
python3 scripts/demo/seed.py --base http://localhost:8080 --log demo.log
python3 scripts/demo/sensors.py cold-break          # primero, antes de cualquier temperatura nueva (issue #9)
python3 scripts/demo/sensors.py door-open --seconds 45
python3 scripts/demo/sensors.py weigh 700           # la leche pasa de 842 g a 650 g
python3 scripts/demo/sensors.py temperature 4.1
python3 scripts/demo/sensors.py door-close
```

Las llaves y contraseñas quedan en `.demo-credentials.json`, en la raíz del repositorio, que está en `.gitignore`.

## Verificación del 11/11/2026

Contra el `web-1.2.0.jar` compilado del commit `e8d28ac`, con PostgreSQL 18 y Redis 8 en Docker y una base vacía:

| Paso | Resultado |
| --- | --- |
| `seed.py` | Hogar Apartment 402 con 7 alimentos, puerta y pesa, receta, presupuesto; Ana unida como MEMBER con alergia al pescado |
| `cold-break` | 5 lecturas aceptadas; Ana recibe `COLD_CHAIN_BREACH` |
| `door-open --seconds 45` | Aceptada; Ana recibe `DOOR_LEFT_OPEN` |
| `weigh 700` | Aceptada; Milk queda en 650 g |
| `temperature 4.1`, `door-close` | Aceptadas |
| `weigh 650 --unstable` | Descartada como inestable (no cambia el stock) |
| Ana usa el yogur privado de Juan | 403, como en la escena 1 |
