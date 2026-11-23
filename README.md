# HayPaComer documentation

The documentation of **HayPaComer**, the smart fridge that answers "what can I cook right now with what is actually at home?". Work happens here and goes straight to `main`; the history up to version 1.1.0 comes from the monorepo [Juansit-0/HayPaComer](https://github.com/Juansit-0/HayPaComer), with each commit kept under its original author, then, the final versions are out on the repos: 

- Backend
[github.com/Juansit-0/HayPaComer-backend](github.com/Juansit-0/HayPaComer-backend)

Java 25, Spring Boot, modules and tests.

- Web
[github.com/Juansit-0/HayPaComer-web](github.com/Juansit-0/HayPaComer-web)

interface, mmodules ES and 3D kitchen

- Database
[github.com/Juansit-0/HayPaComer-db](github.com/Juansit-0/HayPaComer-db)

migrations on Flyway, PostgreSQL and Redis

- Documentation for Desgin Patterns
[github.com/Juansit-0/HayPaComer-docs](github.com/Juansit-0/HayPaComer-docs)

architecture, patterns, and demo

- Firmware
[github.com/Juansit-0/HayPaComer-firmware](github.com/Juansit-0/HayPaComer-firmware
)

ESP32

---

**Planning board:** https://github.com/users/NicoalsD/projects/1 (45 issues in 6 sprints, each assigned to its owner).

**Live app:** https://haypacomer.jenilarper.dev (the landing can take a couple of seconds while the service wakes up).

## What is here

- `docs/`: architecture, data model, REST API, event protocol, GoF patterns, responsible AI, firmware, hardware, demo script, production runbook, ADRs, and the original proposal;
- `brand/`: naming, positioning, voice, identity, and design tokens;
- `PLAN.md` and `CHANGELOG.md`: the master plan and the release history;
- `sprint-3/`: the test plan in the course template (Excel, in Spanish);
- `sprint-4/`: the automated tests (unit, integration, API and browser end-to-end), how they are automated, scripts, results, the final presentation PDF, defects found, and blockers (in Spanish);
- `scripts/demo/`: demo seed and ESP32 simulator, adjusted and verified against v1.2.0.
