# Guion · HayPaComer · Calidad de software

Presentación: `HayPaComer - Calidad (sprint 5)` (13 diapositivas, unos 9 minutos). Lo que está entre comillas se dice en voz alta; lo demás es respaldo y no se lee.

| Integrante | Diapositivas | Tiempo |
| --- | --- | --- |
| Nicolas Diaz | 1, 3, 5, 6 (conceptos generales: tablero, niveles de prueba y automatización) | ~2:30 |
| Jenifer Urbano | 7, 8, 10, 11 (pruebas del proyecto, defectos y agentes de IA) | ~3:05 |
| Juan Camilo Lopez | 2, 4, 9, 12, 13 (el proyecto, sprints, prueba de navegador, equipo y bloqueos) | ~3:15 |

## 1 · Portada · Nicolas (0:20)

> "Buenas. Somos Nicolas, Jenifer y Juan Camilo, y presentamos HayPaComer desde el lado de la calidad: qué pruebas tiene, cómo las automatizamos, qué encontraron, qué hizo la inteligencia artificial y qué nos bloqueó."

## 2 · Qué probamos, en una frase · Juan (0:35)

> "HayPaComer es una nevera inteligente: pesa la comida, vigila la puerta y el frío, y te dice qué cocinar. Varias personas comparten la misma nevera."
>
> "Son cuatro cosas: el inventario en gramos, las casas compartidas con comida privada o de preguntar antes, las alertas y avisos, y una IA que si falla deja todo funcionando con reglas."
>
> "Cada una de esas reglas tiene pruebas automáticas que la defienden. De eso va esta presentación."

## 3 · Tablero en GitHub Projects · Nicolas (0:40)

> "Para planear usamos GitHub Projects en lugar de Jira. Esta es la foto real del tablero."
>
> "Son 45 issues en 6 sprints de dos semanas, y cada uno tiene responsable. Llevamos 40 hechos y 5 en backlog para los sprints 5 y 6."

Si preguntan por qué no Jira: el código ya estaba en GitHub, así que cada issue se enlaza con sus commits sin otra herramienta.

## 4 · Seis sprints · Juan (0:35)

> "Los tres primeros sprints fueron de construir: dominio y sensores, cocina e IA, y rediseño. El sprint 4 fue el de calidad: pruebas completas contra el backend real, el plan de pruebas con 25 de 25 aprobados, el tablero y la demo."
>
> "Ahora estamos en el sprint 5: sumamos casas con código, permisos con notificaciones, que la comida viaje contigo al cambiar de casa, y las pruebas de extremo a extremo."

## 5 · Cinco niveles de pruebas · Nicolas (0:45)

> "Tenemos cinco niveles. Abajo, las unitarias: prueban una clase sola, en memoria, sin base de datos; son la mayoría y corren en segundos."
>
> "Arriba van las de arquitectura, que vigilan que el dominio no dependa de Spring. Luego las de integración, que levantan la app con un PostgreSQL real en Docker."
>
> "Y en la punta, dos pruebas de extremo a extremo: una que usa la API como la app y otra que abre un navegador real."
>
> "En total son 890 pruebas en el backend, 23 en la web y 179 comprobaciones de extremo a extremo."

Palabras clave:
- **Testcontainers:** levanta la base de datos real en Docker durante la prueba y la borra al terminar.
- **ArchUnit:** prueba la arquitectura, no un resultado.

## 6 · Cómo se automatizó · Nicolas (0:45)

> "Nadie corre las pruebas a mano. Cuando alguien hace push, GitHub Actions corre `mvn verify`: compila los 8 módulos y ejecuta las 890 pruebas."
>
> "Además, JaCoCo mide la cobertura: si en el dominio baja del 80 %, el build falla. Si algo falla, no se puede hacer merge y Render no despliega."
>
> "Las pruebas de extremo a extremo son dos scripts que se corren contra el servidor, local o desplegado. Cada línea dice OK o FAIL y al final dan el total."

## 7 · Prueba 1, integración · Jenifer (0:45)

> "La primera prueba que mostramos es de integración. Arranca la app completa con un PostgreSQL de verdad y le hace peticiones como lo haría el navegador."
>
> "Prueba una función nueva: si sales de una casa, tu comida se va contigo. Ana guarda dos latas privadas y leche con fecha. Elimina su casa y se une a la de Beto, y las latas llegan con sus 720 gramos, 360 por unidad, todavía privadas, y la leche con su fecha."
>
> "Además, Beto solo ve las latas de Ana como alimento privado. Resultado: 2 pruebas, 0 fallos."

## 8 · Prueba 2, API de extremo a extremo · Jenifer (0:40)

> "La segunda es un script en Python que usa la API como lo haría la app, con tres personas."
>
> "No solo revisa que responda 200. Revisa las reglas: una persona solo puede estar en una casa, nadie puede aprobar su propia solicitud, responder dos veces da error, y cada notificación le llega solo a quien debe."
>
> "Resultado: 147 de 147 comprobaciones."

## 9 · Prueba 3, navegador con Playwright · Juan (0:45)

> "La tercera abre un navegador real con dos personas. Se registran, crean la casa, configuran la nevera y agregan dos latas. La otra persona se une con el código y pide permiso."
>
> "El dueño ve la notificación en la campana y aprueba, y a quien pidió le llega la respuesta. También prueba que al pasar de celular a pantalla completa no haya que recargar, y que cerrar sesión lleve al login."
>
> "Dio 29 de 32. Los 3 fallos no son de la prueba: son defectos reales que encontró, y los vemos en la siguiente."

## 10 · Lo que encontraron las pruebas · Jenifer (0:50)

> "Una prueba sirve si encuentra cosas. La de navegador encontró dos defectos: las notificaciones de permisos salen en inglés, y la consulta del presupuesto da 404 cuando la casa todavía no tiene uno."

> "Ya sabemos la causa de los dos. No los corregimos en esta entrega porque se trabaja solo en el repositorio de documentación y el código no se toca; por eso los registramos en el tablero como issues del sprint 5, cada uno con su solución y con la prueba que va a confirmar que quedó bien. Ninguno pierde datos ni deja pasar a nadie sin permiso: eso lo confirma la prueba de la API."
>
> "Y estos cuatro ya están resueltos, cada uno con una prueba que evita que vuelva: el tomate duplicado por la IA, el catálogo que se cortaba en 60 alimentos, la casa que no se podía eliminar y la comida vencida que no viajaba."

## 11 · Agentes de IA · Jenifer (0:50)

> "Usamos agentes de IA para programar. Con Claude Code se implementaron los pasos del roadmap de la versión 1.2, y este mes las casas con código, las notificaciones de permisos, el traslado de comida y las unidades. También se hicieron con él los dos scripts de prueba de extremo a extremo y este material."
>
> "OpenCode trabajó con las mismas instrucciones, y la skill Impeccable hizo la auditoría de la interfaz que nos llevó al rediseño."
>
> "Pero la IA no publica sola. Hay un archivo de reglas para el agente, una guía por tarea con su definición de hecho, y el CI bloquea todo si una prueba falla. Las pruebas que escribió la IA también tienen que pasar, y el commit y el push los hacemos nosotros."

## 12 · Quién trabajó en qué · Juan (0:30)

> "Yo llevé el dominio, la web con la nevera 3D, el firmware del ESP32 y el despliegue."
>
> "Jenifer llevó el backend, la base de datos, el agente de IA y la analítica, y este sprint las casas, los permisos, las notificaciones y los scripts de prueba."
>
> "Nicolas llevó QA y el plan de pruebas, el tablero y la presentación. Todo esto sale del tablero, donde cada issue tiene su responsable."

## 13 · Bloqueos y soluciones · Juan, cierre de los tres (0:50)

**Juan:**

> "El bloqueo más serio fue de concurrencia: veinte personas usando la misma leche a la vez respondían OK, pero se perdían gramos. Lo resolvimos con un bloqueo por hogar en PostgreSQL, y una prueba lo vigila en cada build."
>
> "También tuvimos que cambiar SQLite por PostgreSQL, Google retiró el modelo de Gemini que usábamos, ArchUnit se quedaba sin memoria en Docker, y actualizamos las pruebas que defendían la regla vieja de roles."
>
> "Quedan dos abiertos para el sprint 5: el correo en producción y los respaldos de la base gratuita."

**Los tres:**

> "En resumen: 890 pruebas en el backend, 147 de 147 en la API y 29 de 32 en el navegador, con los defectos ya identificados. ¿Preguntas?"

## Preguntas probables

- **¿Por qué 29 de 32 y no 32?** Porque la prueba encontró defectos reales. Preferimos mostrarlo a esconderlo, y ya sabemos la causa de dos de los tres fallos.
- **¿Qué diferencia hay entre integración y extremo a extremo?** La de integración corre dentro del proyecto con una base real. La de extremo a extremo usa el sistema desde fuera, como un usuario, por la API o con un navegador.
- **¿Quién garantiza lo que escribió la IA?** El CI (no entra si una prueba falla) y la revisión del equipo antes del commit.
- **¿Dónde está todo?** En el repositorio de documentación: `pruebas/README.md`, `scripts/qa/` y esta presentación.
