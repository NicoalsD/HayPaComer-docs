# Pruebas automatizadas de HayPaComer

Las pruebas automatizadas existen y viven junto al código que prueban, no en este repositorio de documentación:

| Repositorio | Qué prueba | Cuántas | Cómo se corren |
| --- | --- | --- | --- |
| [HayPaComer-backend](https://github.com/Juansit-0/HayPaComer-backend) | Java: dominio, casos de uso, agente de IA, base de datos, sensores, API | 785 métodos de prueba en 212 archivos; Maven ejecutó 800 el 10/11/2026 (algunas pruebas se repiten con varios datos) | `mvn verify` (necesita Docker para PostgreSQL y Redis) |
| [HayPaComer-web](https://github.com/Juansit-0/HayPaComer-web) | JavaScript de la interfaz: búsqueda de alimentos, dinero, animaciones, calidad | 23 pruebas en 6 archivos, más un chequeo de textos | `npm run check` (usa `node --test`, sin instalar nada) |

No se copiaron aquí a propósito: una copia quedaría desactualizada apenas cambie el código. Los enlaces de abajo apuntan a la versión 1.2.0 del backend (commit `e8d28ac`).

## Explicado fácil

Una prueba automatizada es un pequeño programa que usa el sistema y revisa que el resultado sea el esperado. Por ejemplo: "si la pesa pasa de 700 g a 650 g, el inventario debe bajar 50 g". Si alguien cambia el código y rompe esa regla, la prueba falla y avisa antes de que el error llegue a la app.

Hay tres niveles, del más rápido al más completo:

1. **Unitarias (564 de las 800).** Prueban una regla sola, sin servidor ni base de datos. Corren en milisegundos. Ejemplo: la estrategia FLEXIBLE reduce la receta a una porción cuando hay 80 g de pollo.
2. **Web con MockMvc.** Simulan peticiones HTTP a la API sin abrir un servidor real. Revisan que cada ruta responda bien y que los errores salgan en el formato estándar.
3. **Integración con Testcontainers.** Levantan un PostgreSQL 18 y un Redis 8 reales dentro de Docker y prueban el sistema completo de punta a punta, como en la demo.

Además, hay pruebas de **arquitectura** (ArchUnit): no revisan resultados, sino que el código respete las capas. Por ejemplo, que el dominio no use Spring ni la base de datos.

## Dónde están, por módulo del backend

| Módulo | Archivos | Pruebas | Qué cubre |
| --- | --- | --- | --- |
| `domain` | 50 | 250 | Reglas puras: pesa, recetas, permisos, cadena de frío, vencimientos |
| `application` | 59 | 229 | Casos de uso: consumir, invitar, cocinar, mercado, sensores |
| `agent` | 13 | 70 | Agente de IA: herramientas, validación de argumentos, confirmaciones |
| `adapter-persistence` | 28 | 70 | PostgreSQL y Redis reales (Testcontainers) |
| `web` | 41 | 89 | API REST, seguridad y flujos completos de integración |
| `adapter-ai` | 10 | 40 | Clientes de Gemini y OpenAI, circuit breaker |
| `adapter-sensors` | 9 | 33 | Validación de eventos del ESP32 |
| `adapter-notifications` | 2 | 4 | Telegram y bandeja web |

## Cómo se relacionan con el plan de pruebas

Cada uno de los 25 casos del Excel (`Plan de Pruebas HayPaComer.xlsx`) corresponde a una prueba real del código:

| Caso | Qué comprueba | Prueba |
| --- | --- | --- |
| QA001 | Tara y calibración de la pesa | [ScaleCalibrationTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/scale/ScaleCalibrationTest.java) |
| QA002 | Peso del modo cocina contra la meta (3 %) | [WeighingTargetTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/scale/WeighingTargetTest.java) |
| QA003 | Lectura estable: 1 s dentro de ±2 g | [ScaleCalibrationTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/scale/ScaleCalibrationTest.java) |
| QA004 | La pesa descuenta lo consumido | [FridgeModeDiscountTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/application/src/test/java/dev/haypacomer/application/scale/FridgeModeDiscountTest.java) |
| QA005 | Ignora ruido y lecturas inestables | [FridgeModeDiscountTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/application/src/test/java/dev/haypacomer/application/scale/FridgeModeDiscountTest.java) |
| QA006 a QA008 | Recetas STRICT, FLEXIBLE y RESCUE | [EvaluationStrategyTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/cooking/EvaluationStrategyTest.java) |
| QA009 | Sustituciones que respetan alergias | [SubstitutionCatalogTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/substitution/SubstitutionCatalogTest.java) |
| QA010 | Comida privada necesita permiso | [FoodAccessGuardTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/application/src/test/java/dev/haypacomer/application/inventory/FoodAccessGuardTest.java) |
| QA011 | Permisos por rol OWNER, MEMBER y GUEST | [HouseholdTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/household/HouseholdTest.java) |
| QA012 | Cadena de frío rota pasa a revisión | [ColdChainTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/coldchain/ColdChainTest.java) |
| QA013 | Alerta de puerta abierta a los 40 s | [SensorMonitoringTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/application/src/test/java/dev/haypacomer/application/sensor/SensorMonitoringTest.java) |
| QA014 | Una persona a la vez por nevera | [FridgeSessionTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/fridge/FridgeSessionTest.java) |
| QA015 | Lista de mercado sin duplicados | [MarketListTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/market/MarketListTest.java) |
| QA016 | Plan semanal rescata lo que vence | [WeeklyPlanTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/planning/WeeklyPlanTest.java) |
| QA017 | Vencimiento estimado según dónde se guarda | [ExpiryRulesTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/expiry/ExpiryRulesTest.java) |
| QA018 | Un comando repetido no descuenta dos veces | [LiveInventoryTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/application/src/test/java/dev/haypacomer/application/inventory/LiveInventoryTest.java) |
| QA019 | Deshacer cambios del inventario | [UndoAndSnapshotsTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/application/src/test/java/dev/haypacomer/application/inventory/UndoAndSnapshotsTest.java) |
| QA020 | La IA no puede llamar herramientas con datos inválidos | [ToolRegistryTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/agent/src/test/java/dev/haypacomer/agent/tools/ToolRegistryTest.java) |
| QA021 | Búsqueda de alimentos con errores de digitación | [fuzzy.test.mjs](https://github.com/Juansit-0/HayPaComer-web/blob/main/tools/checks/fuzzy.test.mjs) (web) |
| QC001 | Demo completa de punta a punta | [DemoFlowIntegrationTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/web/src/test/java/dev/haypacomer/web/DemoFlowIntegrationTest.java) |
| QC002 | 20 consumos simultáneos no pierden gramos | [DemoFlowIntegrationTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/web/src/test/java/dev/haypacomer/web/DemoFlowIntegrationTest.java) |
| QC003 | Hogares aislados y roles en la API | [SecurityIntegrationTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/web/src/test/java/dev/haypacomer/web/security/SecurityIntegrationTest.java) |
| QC004 | Cadena de frío guardada en PostgreSQL real | [PostgresColdChainRepositoryTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/adapter-persistence/src/test/java/dev/haypacomer/persistence/relational/PostgresColdChainRepositoryTest.java) |

Pruebas de arquitectura: [DomainBoundariesTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/domain/src/test/java/dev/haypacomer/domain/DomainBoundariesTest.java) y [ApplicationArchitectureTest](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/application/src/test/java/dev/haypacomer/application/ApplicationArchitectureTest.java).

## Cómo se corren solas: el CI

Cada vez que alguien sube código al backend, GitHub Actions ([`ci.yml`](https://github.com/Juansit-0/HayPaComer-backend/blob/e8d28ac/.github/workflows/ci.yml)) hace esto:

1. Instala Java 25 y trae la interfaz web.
2. Corre `mvn -B -ntp verify`: compila y ejecuta todas las pruebas.
3. **JaCoCo** mide qué parte del código se ejecutó durante las pruebas. Si queda por debajo del **80 %**, el build falla.
4. Construye la imagen Docker de producción y revisa que no corra como administrador (root).

Si cualquier paso falla, no se puede hacer merge y Render no despliega. El último CI de la versión 1.2.0 está [en verde](https://github.com/Juansit-0/HayPaComer-backend/actions/runs/42324439173).

## Resultado del 10/11/2026

- **800** pruebas ejecutadas en Docker con JDK 25, **797** aprobadas.
- Los **3** fallos están solo en el módulo `web`. No son errores del código: en la ejecución local no se copió la interfaz estática dentro del `.jar`, un paso que el CI sí hace. El CI del mismo commit está en verde.
- Los 25 casos del plan de pruebas pasaron.

## Lo que falta

- Una prueba de integración por endpoint donde un MEMBER y un GUEST inicien sesión y el servidor les rechace lo que no pueden hacer. Está anotado como siguiente paso en QC003.
- La interfaz web se prueba por funciones sueltas, pero no en un navegador real (no hay pruebas end-to-end de la UI con Playwright o similar).
