# Guía de Jenifer · Las pruebas que explicas, a fondo

Jenifer presenta las diapositivas **7, 8, 10 y 11** (unos 3 minutos). El guion corto está en `guion-calidad.pdf`; esta guía explica **cómo funciona cada prueba por dentro**, para entenderlas, contestar preguntas y correrlas en VS Code.

## 0 · Cómo correr todo en VS Code

1. Abrir la carpeta `~/haypacomer/NicoalsD-HayPaComer-docs` en VS Code.
2. Abrir **Terminal → Run Task…** (o `Ctrl+Shift+P` → "Tasks: Run Task") y elegir la tarea:

| Tarea | Qué hace | Necesita | Dura |
| --- | --- | --- | --- |
| `1. Base de datos (PostgreSQL + Redis en Docker)` | Levanta las dos bases locales | Docker abierto | 5 s |
| `2. Backend en http://localhost:8090` | Arranca la app; queda corriendo en esa terminal | La tarea 1 | 15 s |
| `Prueba 1 · Integración: MovingFoodIntegrationTest` | La prueba de la diapositiva 7 | Docker abierto (no el backend) | ~20 s |
| `Prueba 2 · API de extremo a extremo: smoke_api.py` | La de la diapositiva 8 | El backend | ~1 min |
| `Prueba 3 · Navegador de extremo a extremo: e2e_ui.py` | La de la diapositiva 9 (de Juan) | El backend | ~3 min |
| `Unitarias nuevas: …` | JoinCodeTest, AccessRequestTest, NotificationChannelsTest | Nada | ~10 s |
| `Suite completa del backend: mvn verify` | Las 890 pruebas | Docker | ~12 min |
| `Pruebas de la web: npm run check` | Las 23 de la interfaz | Node | 5 s |
| `Limpiar las cuentas que crean las pruebas` | Borra `tmp-*` y `e2e-*` de la base local | La tarea 1 | 1 s |

Cómo se lee el resultado:
- En Maven, `Tests run: 2, Failures: 0, Errors: 0` y `BUILD SUCCESS` significan que todo pasó.
- En los scripts, cada línea dice `OK` o `FAIL`, y al final sale el total (`147/147 OK`).

## 1 · Diapositiva 7 · Prueba de integración: `MovingFoodIntegrationTest`

### Qué es una prueba de integración

Una prueba unitaria revisa una pieza sola, en memoria. Una de **integración** revisa que varias piezas funcionen **juntas y de verdad**: el controlador web, los casos de uso, el dominio y la base de datos real. Si algo está mal conectado entre ellas, solo esta clase de prueba lo nota.

### Cómo arranca

```java
@SpringBootTest                 // arranca la aplicación Spring completa
@AutoConfigureMockMvc           // permite hacerle peticiones HTTP sin abrir un puerto
@Testcontainers                 // va a usar contenedores de Docker
class MovingFoodIntegrationTest {
  @Container @ServiceConnection
  static final PostgreSQLContainer POSTGRES = new PostgreSQLContainer("postgres:18-alpine");
```

- **Testcontainers** descarga y arranca un **PostgreSQL 18 real** en Docker solo para esta prueba. Flyway aplica las 89 migraciones (todas las tablas) y, al terminar, el contenedor se borra. Por eso la prueba no ensucia la base local.
- **`@ServiceConnection`** le dice a Spring que se conecte a ese contenedor, sin configurar URL ni contraseña.
- **MockMvc** hace peticiones como `POST /api/v1/households/join` igual que el navegador, pero dentro de la misma JVM.

### Las ayudas que usa (para que el test se lea como una historia)

| Ayuda | Qué hace por debajo |
| --- | --- |
| `signUp("ana@moving.test")` | `POST /auth/register` y `POST /auth/login`; devuelve el token `Bearer …` de esa persona |
| `home(ana, "Primera")` | `POST /households` (crea la casa) |
| `fridge(ana, casa)` | `POST /households/{id}/fridges` (nevera estándar) y toma la primera repisa |
| `stock(ana, casa, nevera, "...")` | `POST /households/{id}/items` (guarda un alimento) |
| `code(ana, casa)` | `GET /households/{id}/join-code` (el código para unirse) |
| `inventory(ana, casa)` | `GET /households/{id}/inventory` (lo que esa persona ve en la nevera) |

### La historia que prueba, paso a paso

1. **Ana** crea su casa y guarda **2 latas de cerveza privadas** (720 g, 360 g cada una) y **leche** con fecha. **Carla** se une con el código y guarda **huevos**.
2. **Beto** crea otra casa con tomates.
3. **Carla sale** de la casa de Ana. Se verifica que en la casa de Ana quedan 2 cosas y que los huevos ya no están (`assertEquals(2, …)`, `noneMatch("Egg")`).
4. **Carla se une** a la casa de Beto. Se verifica que los huevos aparecen en la nevera de Beto.
5. **Ana elimina su casa** y se une a la de Beto. Se verifica que:
   - las latas llegan con **720 g** y **360 g por unidad** (siguen siendo 2 latas);
   - siguen siendo **privadas**;
   - la leche llega con **su misma fecha**;
   - Ana ve **4 cosas**: sus 2, los huevos de Carla y los tomates de Beto.
6. **Beto** ve las latas de Ana solo como **"Alimento privado"**, nunca con su nombre.

Una segunda prueba (`foodBroughtToAHomeWithoutAFridgeWaitsForTheFridge`) revisa que, si la casa nueva aún no tiene nevera, la comida espera y entra cuando se configura la nevera.

### Cómo funciona la función que prueba

Al salir, ser sacado o eliminar la casa, el backend **empaca** la comida propia de esa persona en la tabla `carried_food` (migración V88). Al unirse a otra casa o crear su nevera, la **desempaca** en la primera repisa con el mismo comando que usa la app para guardar comida (patrón Command). Así se aplican las mismas reglas de siempre: cantidades, visibilidad y fechas. Si la fecha ya pasó mientras esperaba, se usa una fecha estimada.

**Resultado:** 2 pruebas, 0 fallos, en unos 15 s.

### Si preguntan

- **¿Por qué no simulan la base de datos?** Porque los errores reales estaban en la base, por ejemplo una llave foránea sin borrado en cascada. Con un simulador no se habrían visto.
- **¿No es lenta?** Unos 15 segundos. Las unitarias son milisegundos; por eso hay pocas de integración y muchas unitarias (la pirámide).
- **¿Qué es un `assert`?** La línea que compara lo esperado con lo obtenido. Si no coinciden, la prueba falla y el CI bloquea el cambio.

## 2 · Diapositiva 8 · API de extremo a extremo: `smoke_api.py`

### Qué es

Un script en Python (`scripts/qa/smoke_api.py`) que usa el sistema **desde fuera**, por HTTP, igual que la app web, contra el servidor corriendo (local o desplegado). No conoce el código Java: solo llama a la API y revisa las respuestas. Se llama "smoke" (humo) porque es una pasada rápida por todo para ver si algo "echa humo".

### Cómo funciona por dentro

- Una sola función, `call(método, ruta, cuerpo, token, expect=código)`, hace la petición con `urllib` (de la librería estándar, sin instalar nada) y **anota si el código HTTP fue el esperado**. Cada llamada produce una línea `OK` o `FAIL`.
- Crea **3 cuentas temporales** (`tmp-a`, `tmp-b`, `tmp-c@local.test`) para probar reglas entre personas.
- Algunas comprobaciones no son códigos HTTP sino reglas (`CHECK`): por ejemplo, "A recibe la notificación de la solicitud" revisa el contenido de `GET /notifications`.

### Qué cubre (147 comprobaciones)

| Área | Ejemplos de lo que exige |
| --- | --- |
| Cuentas | Registro, login, refresh, logout; `GET /me` sin sesión da **401** |
| Casas | Crear con casa ya existente da **409**; código falso **400**; el código en minúsculas funciona; unirse estando en otra casa **409** |
| Permisos por rol | Un integrante no puede sacar a nadie ni eliminar la casa (**403**), pero sí renombrarla, montar la nevera o conectar sensores |
| Unidades | Guardar 2 latas con `pieceGrams: 360` y comprobar que el inventario dice 720 g / 360 g; tras usar una, queda una |
| "Preguntar antes" | Consumir sin permiso **403**; pedir permiso **201**; pedir dos veces devuelve la misma solicitud; aprobar la propia **403**; responder dos veces **409**; después de aprobar, consumir **200** |
| Notificaciones | La de la solicitud le llega **solo** al dueño; la de la respuesta, **solo** a quien pidió |
| El resto | Nevera, forma, gemelo digital, mercado, presupuesto, precios, estadísticas, recetas, plan semanal, sesión de cocina, dispositivo simulado e IA (Gemini aprende un alimento y el chef responde) |

**Resultado:** **147 / 147 OK**. Al final, el script elimina la casa que creó.

### Si preguntan

- **¿Qué diferencia hay con la de integración?** La de integración corre dentro del proyecto Java con una base temporal. Esta prueba el sistema ya corriendo, desde fuera, como un cliente real. Sirve incluso contra producción.
- **¿Por qué esperar errores (403, 409)?** Porque probar que algo **no** se puede hacer es tan importante como probar que sí: es la seguridad.

## 3 · Diapositiva 10 · Lo que encontraron las pruebas

La idea que hay que transmitir: **una prueba vale por lo que encuentra.**

| Defecto | Cómo se encontró | Por qué pasaba | Estado |
| --- | --- | --- | --- |
| Notificaciones en inglés ("Food request…") | La prueba de navegador esperaba el texto en español y no lo encontró | El servidor traduce sus frases desde la tabla `message_templates`, y las de permisos se guardaron en `translations` | Abierto, planeado en #46 (sprint 5) |
| 404 en la consola | La prueba de navegador revisa que no haya errores en la consola | `GET /market-budget` responde 404 cuando la casa aún no tiene presupuesto, que es un estado normal | Abierto, planeado en #47 (sprint 5) |
| "Tomate" duplicado | Lo vimos probando y lo confirmó la prueba de navegador | La IA aprendía "Tomate" como alimento nuevo, aparte de "Tomato" | Resuelto: la migración V90 los une, y buscar por el nombre en español devuelve el original |
| El tomate no salía al agregar | Probando la app | El catálogo se cortaba en 60 alimentos y ya hay 72 | Resuelto |
| Eliminar casa daba 409 | `smoke_api.py` | Una llave foránea (`granted_by`) sin borrado en cascada | Resuelto: los permisos se borran primero |
| La comida vencida no viajaba | `MovingFoodIntegrationTest` | Una fecha ya pasada no se aceptaba al desempacar | Resuelto: se usa una fecha estimada |

Cada defecto resuelto queda **vigilado por su prueba**: si alguien lo vuelve a romper, el CI lo bloquea.

### Por qué hay dos abiertos (decirlo así si preguntan)

> "No los corregimos en esta entrega por una restricción: la entrega de Calidad se trabaja solo en el repositorio de documentación, y los repositorios de código no se tocan. Lo correcto en calidad no es esconderlos: los documentamos con su causa y los registramos en el tablero como issues 46 y 47 del sprint 5, cada uno con su solución y con la prueba que va a confirmar que quedó resuelto."

- **#46, notificaciones en inglés:** una migración nueva (V91) copia las frases a la tabla correcta. Se verifica con una prueba de integración y con `e2e_ui.py`.
- **#47, el 404:** la API responde 204, sin contenido, cuando no hay presupuesto, en vez de 404. Se verifica actualizando `smoke_api.py` y con `e2e_ui.py`.
- **Ninguno pierde datos ni deja pasar a nadie sin permiso:** las 147 comprobaciones de la API lo confirman. Son un idioma y un mensaje en la consola.

## 4 · Diapositiva 11 · Qué se hizo con agentes de IA

| Agente | Qué parte |
| --- | --- |
| **Claude Code** | Pasos del roadmap de la v1.2. En noviembre: casas con código, una casa por persona, notificaciones de permisos, traslado de comida, cantidades por unidades y su dibujo, la corrección del catálogo; los scripts `smoke_api.py` y `e2e_ui.py`; la documentación y esta presentación |
| **OpenCode** | Las mismas tareas con las mismas instrucciones (`AGENTS.md`) y las mismas 19 skills |
| **Impeccable** | La auditoría de la interfaz (24/40) que llevó al rediseño |

**Cómo se controla:**
1. `AGENTS.md` dice qué puede hacer el agente.
2. Cada tarea tiene una guía con su definición de hecho.
3. El agente corre las pruebas; si algo falla, lo corrige antes de entregar.
4. El **CI es obligatorio**: si una prueba falla, no hay merge.
5. **Nosotras y nosotros revisamos**, y el commit y el push los hace el equipo.

**Ejemplo real:** al pedirle a la IA que diera los mismos permisos a todos, una decena de pruebas fallaron porque exigían la regla vieja. La IA no las borró: se revisó cada una, y como la regla cambió a propósito, se actualizaron para exigir la regla nueva.

### Si preguntan

- **¿La IA escribió las pruebas?** Muchas sí, pero tienen que pasar en el CI igual que las demás, y las revisamos. Las pruebas son justamente lo que nos permite confiar en lo que escribe la IA.
- **¿La app usa IA?** Sí, Gemini para el chef y para reconocer alimentos nuevos. Si falla, un circuit breaker pasa a reglas offline y nada se cae.

## 5 · Glosario rápido

- **JUnit:** la librería con la que se escriben y corren las pruebas en Java.
- **MockMvc:** hace peticiones HTTP a la app sin abrir un puerto.
- **Testcontainers:** arranca bases de datos reales en Docker durante la prueba.
- **Flyway / migración:** archivos numerados (V1…V90) que construyen y cambian las tablas.
- **CI (GitHub Actions):** corre todas las pruebas en cada push.
- **JaCoCo:** mide qué parte del código ejecutaron las pruebas; si baja del 80 %, falla.
- **Extremo a extremo (E2E):** probar el sistema completo desde fuera, como un usuario.
- **Smoke test:** una pasada rápida por todo para detectar lo que esté roto.
- **Playwright:** controla un navegador real desde un script.
