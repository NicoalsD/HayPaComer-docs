# Guion de Jenifer - HayPaComer

11 de noviembre de 2026

Jenifer presenta 4 diapositivas propias (8, 10, 11 y 13), unos 2 min 35 s en total. Además comparte la 7 con Juan y la 16 con Nicolas, y en la demo hace de Ana. Las frases entre comillas son para decir en voz alta; lo demás es respaldo y no se lee.

## Diapositiva 8: tecnologías (0:30)

Idea central: cada capa usa una herramienta escogida por una razón concreta.

**Decir:**

> "El backend está hecho en Java 25 con Spring Boot y lo dividimos en 8 módulos, cada uno con una sola responsabilidad."
>
> "Usamos dos bases de datos. PostgreSQL 18 guarda todo lo del hogar: usuarios, comida, gramos, recetas. Flyway lleva el historial de cambios de esa base, y hoy son 71 migraciones. Redis 8 es la memoria rápida de la IA: conversaciones, trazas y caché."
>
> "La web no usa framework ni compilación. Son archivos JavaScript que Spring sirve directamente, con Three.js para la nevera 3D y SSE para que las alertas lleguen en vivo."
>
> "El hardware es un ESP32 con sensor de puerta, sonda de temperatura y una pesa. La IA puede ser Gemini o una API compatible con OpenAI, pero por defecto funciona con reglas, sin internet."

**Palabras que conviene entender:**

- **Flyway:** el "control de versiones" de la base de datos. Cada cambio a las tablas es un archivo numerado (V1, V2...).
- **SSE:** el servidor le avisa al navegador apenas pasa algo, sin que la página tenga que preguntar todo el tiempo.
- **Reglas offline:** si no hay IA, el Chef responde con reglas escritas en Java.

## Diapositiva 10: reglas de recetas (0:50)

Idea central: la receta se evalúa contra los gramos reales, y lo decide Java, no la IA. Es la diapositiva más larga, así que hay que ir despacio.

**Decir:**

> "Tomemos un ejemplo: arroz con pollo para 2 personas pide 200 gramos de pollo, pero la pesa mide 80. El sistema tiene tres formas de evaluarlo; eso es el patrón Strategy."
>
> "STRICT, el estricto, dice exactamente cuánto falta: 120 gramos."
>
> "FLEXIBLE baja las porciones con una tolerancia de cocina del 25 %. Una porción pide 100 gramos; con la tolerancia basta con 75, y hay 80. Entonces la respuesta es: alcanza para una porción."
>
> "RESCUE busca un reemplazo en el catálogo: atún por pollo, uno a uno, hasta 300 gramos. Pero respeta las alergias: si Ana, que es alérgica al pescado, va a comer, el atún desaparece de la sugerencia."
>
> "Las demás reglas también son datos guardados en la base de datos, no código fijo: la alerta de puerta a los 40 segundos, la temperatura segura de 5 grados con 20 minutos de gracia, y la cadena de frío. Cada hogar las puede ajustar."

| Modo | Qué hace | Resultado con 80 g |
| --- | --- | --- |
| STRICT | Dice cuánto falta | Faltan 120 g |
| FLEXIBLE | Reduce porciones (25 % de tolerancia) | 1 porción |
| RESCUE | Busca sustituto según alergias | Atún, o nada si come Ana |

**Si preguntan:** en la demo se pesan 130 g de atún aunque la regla pide 120 g. La prueba unitaria de RESCUE (QA008) usa una regla de prueba distinta (1,1 y 200 g); la regla real de la app (1:1 y 300 g) está en la migración V11.

## Diapositiva 11: roles y permisos (0:30)

Idea central: los permisos son por hogar y por alimento, y el ESP32 tiene su propia llave aparte.

**Decir:**

> "Cada hogar tiene tres roles. El OWNER, el dueño, puede hacer todo: manejar miembros, neveras y dispositivos. El MEMBER edita el inventario, cocina y usa la lista de mercado. El GUEST, el invitado, solo ve el hogar y maneja su propia comida."
>
> "Además, cada alimento tiene dueño. Puede ser privado, compartido o 'pregúntame primero', y se le puede dar permiso a una persona concreta. Lo vamos a ver en la demo con el yogur de Juan."
>
> "El ESP32 no inicia sesión como una persona. Tiene su propia llave, que se puede revocar y que solo sirve para enviar datos de sensores. La llave del dispositivo no sirve para lo de las personas, ni al revés."

**Si preguntan:** los permisos están en el dominio, en dos enums (`Role` y `Permission`), y son 10 en total. El OWNER tiene los 10, el MEMBER 5 y el GUEST 2. Lo prueban QA011 (permisos por rol) y QC003 (aislamiento entre hogares) del plan de pruebas.

## Diapositiva 13: API REST (0:45)

Idea central: 128 "puertas" documentadas por las que la web, el teléfono y el ESP32 hablan con el servidor.

**Decir:**

> "El servidor ofrece 128 operaciones, agrupadas en autenticación, hogar, inventario, dispositivos y pesa, recetas y cocina, mercado, analítica, el agente y tiempo real."
>
> "Para entrar, una persona recibe un pase, un JWT, que dura 15 minutos y se renueva solo. El ESP32 usa su llave de dispositivo."
>
> "Todos los errores salen en el mismo formato estándar, el RFC 7807, y todo está documentado en Swagger, en /docs, donde se puede probar cada operación."
>
> "Hacia afuera hablamos con Gemini, con APIs compatibles con OpenAI y con Telegram. Las claves secretas nunca salen del servidor."

**Si preguntan por qué 128:** el plan estimaba unas 95 y la documentación lista 149 filas, pero algunas no están implementadas. 128 es lo que hay en el código: 49 GET, 52 POST, 11 PUT, 6 PATCH y 10 DELETE.

**Otros respaldos:** el refresh token rota en cada uso y detecta si alguien lo reutiliza. Las escrituras de inventario aceptan un `Idempotency-Key`: si se reintenta la misma petición, no se descuenta dos veces.

## Partes compartidas

**Diapositiva 7, agentes de IA (con Juan, 0:50).** La debe decir quien trabajó con Claude Code y OpenCode. Juan y Jenifer deciden quién la presenta.

> "Usamos Claude Code y OpenCode. El repositorio tiene un archivo AGENTS.md con las instrucciones para cualquier agente. El agente creaba la rama, implementaba y corría las pruebas; nosotros revisábamos, hacíamos push e integrábamos a mano. El CI bloquea el merge si algo falla."

**Diapositiva 16, bloqueos (con Nicolas).** A Jenifer le toca la parte de base de datos:

> "Empezamos con SQLite, pero solo deja escribir a uno a la vez, y aquí escriben la web, el ESP32 y el agente al mismo tiempo. Por eso pasamos a PostgreSQL con Flyway."
>
> "El bug más serio fue de concurrencia: 20 consumos de 50 gramos al mismo tiempo respondieron todos 'OK', pero solo se descontaron 150 gramos. Lo arreglamos con un bloqueo por hogar: ahora pasan exactamente 16, los otros 4 se rechazan por falta de stock y quedan 42 gramos. La prueba QC002 lo revisa en cada build."

**Demo, diapositiva 18 (propuesta, sin confirmar).** Jenifer hace de **Ana** (MEMBER) en el teléfono.

1. Ana intenta usar el yogur privado de Juan y le sale denegado.
2. Juan le da permiso desde el laptop.
3. Ana vuelve a intentar y ya puede usarlo.

## Si preguntan

### ¿Por qué la web no usa framework y está en JavaScript y no en TypeScript?

Lo que está documentado: la web son módulos de JavaScript "sin paso de compilación" que Spring sirve directamente (README de HayPaComer-web). El ADR 0003 eligió una web servida por el mismo backend, con SSE, en lugar de una app de escritorio en JavaFX, para no sumar infraestructura y poder abrirla en cualquier navegador o teléfono. Ningún documento explica por qué no se usó TypeScript, así que las razones de abajo son deducidas y conviene que Juan, que llevó la web, las confirme.

> "La web la sirve el mismo servidor Java, sin herramientas extra. TypeScript o un framework como React necesitan un paso de compilación con Node y npm. Sin eso, todo el sistema se construye con Maven y sale en un solo archivo .jar. Además, el equipo es fuerte en Java, y la lógica importante, como gramos, reglas y permisos, vive en el backend y no en el navegador."

Si insisten: lo que se gana con TypeScript son tipos en el navegador, pero aquí las validaciones que importan ya las hace Java en el servidor.

### ¿Hay una interfaz de administrador?

No hay un administrador general del sistema. El "administrador" es el **OWNER** de cada hogar. No tiene una pantalla aparte: dentro de **Ajustes** le aparecen opciones extra que el resto no ve, y se las esconde el código de la web (`settings.js` y `fridge.js`):

- invitar personas y elegir si entran como MEMBER o GUEST
- cambiar el rol de alguien, pasarle el hogar a otro OWNER o sacar a un miembro
- cambiar los valores de las reglas (alerta de puerta, temperatura, etc.)
- dibujar la forma de la nevera

Las cinco pantallas (Ahora, Nevera, Mercado, Números, Chef) son las mismas para todos. El único otro "rol" es el del ESP32 (`ROLE_DEVICE`), que no es una persona.

### ¿Se puede entrar como invitado? ¿Está documentado y probado?

**Sí se puede, y es real.** El OWNER invita desde Ajustes eligiendo GUEST, o le cambia el rol a alguien que ya está. Nadie puede ser invitado directamente como OWNER: el servidor responde con error 400.

**Documentado:** sí. `docs/api.md` tiene una columna de acceso con el nivel "guest" para cada operación, y los roles aparecen también en `architecture.md` y `database.md`.

**Probado:** en parte.

- **Sí:** pruebas unitarias del dominio (QA011, `HouseholdTest`: el GUEST puede ver el hogar pero no cocinar) y cerca de 20 pruebas de casos de uso que incluyen a un invitado. Por ejemplo, un invitado puede guardar comida privada pero no compartida.
- **Sí:** pruebas de integración que crean una invitación GUEST y cambian el rol de alguien a GUEST.
- **No:** ninguna prueba de integración donde un invitado inicie sesión y el servidor le rechace una acción de punta a punta. El propio plan de pruebas lo deja anotado como pendiente en QC003: "agregar prueba de roles MEMBER y GUEST por endpoint".
- **Ojo:** la web no esconde los botones de editar para el invitado. Si un GUEST los toca, es el servidor el que lo rechaza.

> "El rol invitado existe y está probado en el dominio. Lo que falta es una prueba de punta a punta por cada endpoint, y eso está anotado en el plan de pruebas como siguiente paso."

En la demo no aparece ningún invitado: solo Juan (OWNER) y Ana (MEMBER).

### ¿Cuántas bases de datos y cuántas tablas?

> "Dos. PostgreSQL 18 guarda todo lo del hogar en 46 tablas, más particiones mensuales para las lecturas de sensores, creadas con 71 migraciones. Redis 8 guarda el estado de la IA."

### ¿Qué pasa con Redis si se cierra el Chef?

> "No se borra nada al cerrar el Chef. Cada dato tiene su propio tiempo de vida: las conversaciones duran 7 días, las trazas del agente 30 días y las confirmaciones pendientes 10 minutos. Si Redis se perdiera completo, se pierde el historial de la IA, pero nunca el inventario ni los gramos, porque eso está en PostgreSQL."

En local Redis guarda en disco cada segundo. En el plan gratis de Render probablemente no: sin confirmar.

## Por confirmar y fuentes

- [ ] Quién presenta la diapositiva 7 (Juan o Jenifer)
- [ ] Si Jenifer hace de Ana en la demo
- [ ] Que Juan confirme por qué la web no usa framework ni TypeScript (no está documentado)
- [ ] Si Redis de Render guarda en disco en el plan gratis

Fuentes: notas del orador de `HayPaComer - Presentacion.pptx`, `Plan de Pruebas HayPaComer.xlsx` y los repositorios públicos [HayPaComer-backend](https://github.com/Juansit-0/HayPaComer-backend), [HayPaComer-db](https://github.com/Juansit-0/HayPaComer-db), [HayPaComer-web](https://github.com/Juansit-0/HayPaComer-web) y [HayPaComer-docs](https://github.com/Juansit-0/HayPaComer-docs) (ADR 0003, 0014, 0015 y `docs/api.md`).
