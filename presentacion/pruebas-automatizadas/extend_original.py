"""Agrega al deck original (sprint 4) las diapositivas de pruebas: stack, resultados, cada prueba con su captura real y defectos.

Uso: python3 extend_original.py <original.pptx> <salida.pptx> <carpeta-de-capturas>
Inserta 7 diapositivas después de "Plan de pruebas" (la 17) y deja las demás igual.
"""
import copy
import sys

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt

SRC, OUT, IMG = sys.argv[1], sys.argv[2], sys.argv[3]
prs = Presentation(SRC)
IN = 914400
PAPEL = RGBColor(0xF3, 0xEC, 0xDF); CARTA = RGBColor(0xFB, 0xF6, 0xEC); BEIGE = RGBColor(0xE8, 0xDF, 0xCC)
TINTA = RGBColor(0x1C, 0x17, 0x12); PIEDRA = RGBColor(0x5C, 0x55, 0x4C); TOMATE = RGBColor(0xC8, 0x43, 0x2A)
CILANTRO = RGBColor(0x2F, 0x7A, 0x4A); MORA = RGBColor(0x4B, 0x1F, 0x2E); COBRE = RGBColor(0xA8, 0x48, 0x1F)
PAPA = RGBColor(0xF3, 0xC4, 0x43); BLANCO = RGBColor(0xFF, 0xFF, 0xFF)

model = prs.slides[16]                      # "Plan de pruebas": su layout, título y número
layout = model.slide_layout
number_sp = next(sh._element for sh in model.placeholders if sh.placeholder_format.type == 13)
title_font = model.placeholders[100].text_frame.paragraphs[0].runs[0].font


def i(x):
    return Emu(int(x * IN))


def text(s, x, y, w, h, lines, size=16, align=PP_ALIGN.LEFT):
    tf = s.shapes.add_textbox(i(x), i(y), i(w), i(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    for n, line in enumerate(lines if isinstance(lines, list) else [lines]):
        p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
        p.alignment = align
        for chunk, bold, color in (line if isinstance(line, list) else [(line, False, TINTA)]):
            r = p.add_run(); r.text = chunk; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = "Calibri"
        p.space_after = Pt(size * 0.3)


def card(s, x, y, w, h, fill=CARTA):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, i(x + 0.06), i(y + 0.06), i(w), i(h)); sh.adjustments[0] = 0.08
    sh.fill.solid(); sh.fill.fore_color.rgb = TINTA; sh.line.fill.background()
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, i(x), i(y), i(w), i(h)); c.adjustments[0] = 0.08
    c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.color.rgb = TINTA; c.line.width = Pt(1.5)


def pic(s, path, x, y, mw, mh, label):
    im = Image.open(path); r = min(mw / (im.width / 100), mh / (im.height / 100)); w, h = im.width / 100 * r, im.height / 100 * r
    p = s.shapes.add_picture(path, i(x + (mw - w) / 2), i(y), i(w), i(h)); p.line.color.rgb = TINTA; p.line.width = Pt(1.25)
    text(s, x + (mw - w) / 2, y + h + 0.03, w, 0.28, [[(label, True, PIEDRA)]], size=10)


def new(title, notes):
    s = prs.slides.add_slide(layout)
    t = s.placeholders[100].text_frame
    t.text = title
    r = t.paragraphs[0].runs[0]; r.font.name = title_font.name; r.font.size = title_font.size; r.font.bold = title_font.bold
    s.shapes._spTree.append(copy.deepcopy(number_sp))
    s.notes_slide.notes_text_frame.text = notes
    return s


def table(s, x, y, w, rows, widths, head, size=14, color_last=None):
    t = s.shapes.add_table(len(rows) + 1, len(head), i(x), i(y), i(w), i(0.4 * (len(rows) + 1))).table
    for j, (h, wd) in enumerate(zip(head, widths)):
        t.columns[j].width = i(wd); c = t.cell(0, j); c.text = h; c.fill.solid(); c.fill.fore_color.rgb = TINTA
        r = c.text_frame.paragraphs[0].runs[0]; r.font.color.rgb = BLANCO; r.font.bold = True; r.font.size = Pt(size)
    for k, row in enumerate(rows, 1):
        for j, v in enumerate(row):
            c = t.cell(k, j); c.text = v; c.fill.solid(); c.fill.fore_color.rgb = CARTA if k % 2 else BEIGE
            r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(size); r.font.color.rgb = TINTA; r.font.bold = j == 0
            if color_last and j == len(row) - 1:
                c.fill.fore_color.rgb = color_last(v); r.font.color.rgb = BLANCO; r.font.bold = True
    return t


added = []

# A · stack de pruebas
s = new("Con qué hicimos las pruebas", "Nicolas: Este es el stack de pruebas. En Java, JUnit escribe y corre cada prueba, MockMvc hace las peticiones a la API, Testcontainers levanta bases de datos reales en Docker, ArchUnit vigila la arquitectura y JaCoCo mide la cobertura. Afuera, un script en Python prueba la API y Playwright prueba con un navegador real. GitHub Actions corre todo en cada push, y en VS Code cada prueba es una tarea.")
table(s, 0.6, 1.35, 12.13, [
    ("JUnit 6", "Escribir y correr cada prueba (@Test, asserts)", "Backend: unitarias, integración, API"),
    ("MockMvc", "Peticiones HTTP a la app sin abrir un puerto", "Pruebas de la API e integración"),
    ("Testcontainers + Docker", "PostgreSQL 18 y Redis 8 reales durante la prueba", "Integración"),
    ("ArchUnit", "Que el dominio no dependa de Spring; 1 método por caso de uso", "Arquitectura"),
    ("JaCoCo", "Cobertura; el build falla si baja del 80 %", "domain, application, agent"),
    ("Maven (Surefire)", "Corre las 890 pruebas: mvn verify", "Backend, en local y en el CI"),
    ("node --test", "23 pruebas y revisión de textos de la interfaz", "Web: npm run check"),
    ("Python 3 (urllib)", "smoke_api.py: 147 comprobaciones contra la API encendida", "API de extremo a extremo"),
    ("Playwright + Chromium", "e2e_ui.py: navegador real con dos personas", "Navegador de extremo a extremo"),
    ("GitHub Actions · VS Code", "CI en cada push · tareas para correr cada prueba", "Automatización"),
], [2.9, 5.6, 3.63], ["Herramienta", "Para qué", "Dónde"], size=13)
added.append(s)

# B · resumen de resultados
ok = lambda v: TOMATE if v.startswith("29") or v.startswith("30") else CILANTRO
s = new("Resultados de las pruebas (20 al 23 de noviembre)", "Nicolas: Estos son los resultados actuales. La suite del backend tiene 890 pruebas; las unitarias e integración nuevas pasan todas; la prueba de la API da 147 de 147, y la de navegador 29 de 32 porque encontró dos defectos reales, que vemos más adelante.")
table(s, 0.6, 1.35, 12.13, [
    ("Suite completa del backend", "mvn verify · 8 módulos", "890 pruebas"),
    ("Interfaz web", "npm run check · node --test", "23 / 23"),
    ("Unitarias nuevas", "JoinCode, AccessRequest, NotificationChannels", "12 / 12"),
    ("Integración", "MovingFoodIntegrationTest · PostgreSQL real", "2 / 2"),
    ("API de extremo a extremo", "smoke_api.py · 3 personas", "147 / 147"),
    ("Navegador de extremo a extremo", "e2e_ui.py · Playwright · 2 personas", "29 / 32"),
    ("Plan de pruebas (Excel del curso)", "31 casos: 25 de la v1.2.0 + 6 nuevos", "30 / 31"),
], [3.9, 5.6, 2.63], ["Prueba", "Cómo", "Resultado"], size=15, color_last=ok)
text(s, 0.6, 5.2, 12.13, 1.3, [[("Los fallos del navegador no son de la prueba: ", True, TOMATE), ("son 2 defectos reales que encontró (issues #46 y #47 del sprint 5). ", False, TINTA)],
                                [("Capturas, scripts y salidas completas: pruebas/README.md en el repositorio de documentación.", False, PIEDRA)]], size=15)
added.append(s)


def test_slide(title, code, res, what, checks, result, color, notes):
    s = new(title, notes)
    pic(s, f"{IMG}/{code}.png", 0.6, 1.3, 6.0, 2.65, "Código, en VS Code")
    pic(s, f"{IMG}/{res}.png", 0.6, 4.3, 6.1, 2.3, "Resultado, en la terminal (23/11/2026)")
    card(s, 6.95, 1.3, 5.78, 5.35)
    lines = [[("Qué es", True, COBRE)], [(what, False, TINTA)], [("Qué verifica", True, COBRE)]]
    lines += [[("• " + c, False, TINTA)] for c in checks] + [[("Resultado", True, COBRE)], [(result, True, color)]]
    text(s, 7.2, 1.45, 5.3, 5.1, lines, size=15)
    added.append(s)


test_slide("Pruebas unitarias: código de casa y permisos", "unit-code", "unit-res",
           "Prueban una sola clase en memoria, sin base de datos ni red. Tardan milisegundos.",
           ["JoinCodeTest: 8 caracteres sin O, 0, I ni 1; nunca da el rol de dueño",
            "AccessRequestTest: una solicitud se responde una vez; nadie se pide permiso a sí mismo",
            "NotificationChannelsTest: la respuesta le llega solo a quien pidió"],
           "12 pruebas, 0 fallos · BUILD SUCCESS en 3 s", CILANTRO,
           "Nicolas: Las unitarias prueban una clase sola, en memoria. Aquí, el código para unirse a una casa y las solicitudes de permiso. Doce de doce, en tres segundos.")
test_slide("Prueba de integración: la comida viaja con su dueño", "int-code", "int-res",
           "Arranca la app completa con un PostgreSQL 18 real en Docker (Testcontainers) y le hace peticiones con MockMvc.",
           ["Quien sale de una casa se lleva su comida; al unirse a otra entra a esa nevera",
            "Las latas llegan con 720 g, 360 g por unidad, y siguen privadas",
            "La leche llega con su fecha; el otro solo ve \"Alimento privado\""],
           "2 pruebas, 0 fallos · BUILD SUCCESS", CILANTRO,
           "Jenifer: La primera prueba que mostramos es de integración. Arranca la app completa con un PostgreSQL de verdad. Ana guarda dos latas privadas y leche con fecha, elimina su casa y se une a la de Beto: las latas llegan con 720 gramos, 360 por unidad, todavía privadas, y la leche con su fecha. Dos pruebas, cero fallos.")
test_slide("Prueba de la API, de extremo a extremo", "api-code", "api-res",
           "smoke_api.py: un script en Python que usa el sistema encendido, desde fuera, por HTTP, con tres personas.",
           ["Lo permitido responde bien y lo prohibido se rechaza (401, 403, 409)",
            "Una persona solo puede estar en una casa",
            "Cada notificación le llega solo a quien debe",
            "Gemini aprende un alimento y el chef responde"],
           "147 de 147 comprobaciones OK", CILANTRO,
           "Jenifer: La segunda es un script en Python que usa la API como lo haría la app, con tres personas. No solo revisa que responda 200: revisa las reglas, incluido lo que debe rechazarse. 147 de 147.")
test_slide("Prueba en el navegador, de extremo a extremo", "e2e-code", "e2e-res",
           "e2e_ui.py: Playwright abre un navegador real y usa la app como dos personas.",
           ["Registro, casa, nevera y 2 latas por unidades",
            "Unirse con el código y pedir permiso",
            "La notificación le llega al dueño, aprueba y responde",
            "Cada pestaña carga, al agrandar la pantalla y al cerrar sesión"],
           "29 de 32: los 3 fallos son 2 defectos reales", TOMATE,
           "Juan: La tercera abre un navegador real con dos personas y hace el recorrido completo. Dio 29 de 32: los 3 fallos son defectos reales que encontró, en la siguiente.")

# G · defectos y plan
s = new("Lo que encontraron las pruebas, y el plan", "Jenifer: Una prueba sirve si encuentra cosas. La de navegador encontró dos defectos. No los corregimos en esta entrega porque se trabaja solo en el repositorio de documentación; quedaron como issues 46 y 47 del sprint 5, con su solución y la prueba que lo va a confirmar. Ninguno pierde datos ni deja pasar a nadie sin permiso. Y otros cuatro ya están resueltos, cada uno con su prueba.")
for k, (iss, t1, cause, plan) in enumerate([
        ("#46", "Notificaciones en inglés", "Las frases se guardaron en la tabla translations y el servidor traduce desde message_templates.", "Migración V91 que las mueve; prueba de integración en español; e2e_ui.py vuelve a pasar."),
        ("#47", "404 de /market-budget", "Sin presupuesto, la API responde 404 en vez de 204 y la consola lo marca como error.", "Responder 204; actualizar smoke_api.py; e2e_ui.py sin errores de consola.")]):
    x = 0.6 + k * 4.05
    card(s, x, 1.35, 3.8, 3.75)
    text(s, x + 0.25, 1.5, 3.35, 3.6, [[(f"Issue {iss} · Planeado, sprint 5", True, TOMATE)], [(t1, True, TINTA)], [("Por qué pasa", True, COBRE)], [(cause, False, TINTA)], [("Plan", True, COBRE)], [(plan, False, TINTA)]], size=13)
card(s, 8.7, 1.35, 4.03, 3.75)
text(s, 8.95, 1.5, 3.6, 3.6, [[("Resueltos, con su prueba", True, CILANTRO)],
                              [("• \"Tomate\" duplicado por la IA (migración V90)", False, TINTA)],
                              [("• El catálogo se cortaba en 60 alimentos", False, TINTA)],
                              [("• Eliminar una casa daba 409", False, TINTA)],
                              [("• La comida vencida no viajaba a la nueva casa", False, TINTA)]], size=13)
card(s, 0.6, 5.35, 12.13, 1.2, fill=MORA)
text(s, 0.9, 5.5, 11.6, 1.0, [[("No se corrigen aquí: la entrega solo edita el repositorio de documentación. ", True, PAPA), ("Se documentan, se registran en el tablero y se planean, con la prueba que confirmará la solución. Ninguno pierde datos ni salta permisos: lo confirma la prueba de la API.", False, BLANCO)]], size=15)
added.append(s)

# Mover las nuevas justo después de "Plan de pruebas" (posición 17).
ids = prs.slides._sldIdLst
new_ids = [ids[-k] for k in range(len(added), 0, -1)]
for el in new_ids:
    ids.remove(el)
for offset, el in enumerate(new_ids):
    ids.insert(17 + offset, el)
prs.save(OUT)
print("ok", len(prs.slides))
