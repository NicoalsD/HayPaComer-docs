"""Deck corto solo de pruebas automatizadas, con capturas reales de la grabación del 23/11/2026."""
import sys
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt

OUT, IMG, CI = sys.argv[1], sys.argv[2], sys.argv[3]
PAPEL = RGBColor(0xF3, 0xEC, 0xDF); CARTA = RGBColor(0xFB, 0xF6, 0xEC); TINTA = RGBColor(0x1C, 0x17, 0x12)
PIEDRA = RGBColor(0x5C, 0x55, 0x4C); TOMATE = RGBColor(0xC8, 0x43, 0x2A); CILANTRO = RGBColor(0x2F, 0x7A, 0x4A)
PAPA = RGBColor(0xF3, 0xC4, 0x43); MORA = RGBColor(0x4B, 0x1F, 0x2E); COBRE = RGBColor(0xA8, 0x48, 0x1F); BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
prs = Presentation(); prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
IN = 914400
TOTAL = 8


def i(x):
    return Emu(int(x * IN))


def text(s, x, y, w, h, lines, size=16, align=PP_ALIGN.LEFT, font="Calibri"):
    tf = s.shapes.add_textbox(i(x), i(y), i(w), i(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    for n, line in enumerate(lines if isinstance(lines, list) else [lines]):
        p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
        p.alignment = align
        for chunk, bold, color in (line if isinstance(line, list) else [(line, False, TINTA)]):
            r = p.add_run(); r.text = chunk; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = font
        p.space_after = Pt(size * 0.35)


def card(s, x, y, w, h, fill=CARTA):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, i(x + 0.06), i(y + 0.06), i(w), i(h)); sh.adjustments[0] = 0.08
    sh.fill.solid(); sh.fill.fore_color.rgb = TINTA; sh.line.fill.background()
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, i(x), i(y), i(w), i(h)); c.adjustments[0] = 0.08
    c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.color.rgb = TINTA; c.line.width = Pt(2)


def pic(s, path, x, y, mw, mh, label=None):
    im = Image.open(path); r = min(mw / (im.width / 100), mh / (im.height / 100)); w, h = im.width / 100 * r, im.height / 100 * r
    px = x + (mw - w) / 2
    p = s.shapes.add_picture(path, i(px), i(y), i(w), i(h)); p.line.color.rgb = TINTA; p.line.width = Pt(1.5)
    if label:
        text(s, px, y + h + 0.05, w, 0.3, [[(label, True, PIEDRA)]], size=11)


def slide(title, n, notes):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = PAPEL
    if title:
        text(s, 0.6, 0.35, 12.1, 0.9, [[(title, True, TINTA)]], size=28, font="Cambria")
        text(s, 0.6, 7.05, 7, 0.3, "HayPaComer · Pruebas automatizadas", size=11)
        text(s, 11.7, 7.05, 1.0, 0.3, f"{n} / {TOTAL}", size=11, align=PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = notes
    return s


def test_slide(n, title, code, res, what, checks, result, color, notes):
    s = slide(title, n, notes)
    pic(s, f"{IMG}/{code}.png", 0.6, 1.3, 6.0, 2.65, "Código, en VS Code")
    pic(s, f"{IMG}/{res}.png", 0.6, 4.3, 6.1, 2.35, "Resultado, en la terminal")
    card(s, 6.95, 1.3, 5.8, 5.5)
    lines = [[("Qué es", True, COBRE)], [(what, False, TINTA)], [("Qué verifica", True, COBRE)]]
    lines += [[("• " + c, False, TINTA)] for c in checks]
    lines += [[("Resultado (23/11/2026)", True, COBRE)], [(result, True, color)]]
    text(s, 7.2, 1.45, 5.35, 5.2, lines, size=15)


# 1 · portada
s = slide(None, 1, "Nicolas: Presentamos solo las pruebas automatizadas de HayPaComer: qué tipos hay, cómo se automatizan y qué encontraron.")
text(s, 0.75, 2.1, 11, 1.2, [[("Pruebas automatizadas", True, TINTA)]], size=54, font="Cambria")
text(s, 0.75, 3.25, 11, 0.6, [[("HayPaComer · Calidad de software", True, COBRE)]], size=26)
text(s, 0.75, 4.1, 11, 1.0, "Unitarias, de integración, de la API y del navegador: cómo se escriben, cómo corren solas y qué resultado dieron.", size=19)
text(s, 0.75, 5.6, 11, 0.5, [[("Nicolas Diaz · Jenifer Urbano · Juan Camilo Lopez", True, TINTA)]], size=18)
for k, c in enumerate([CILANTRO, PAPA, COBRE, TOMATE]):
    b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, i(0.75 + k * 0.9), i(1.6), i(0.75), i(0.14)); b.fill.solid(); b.fill.fore_color.rgb = c; b.line.fill.background()

# 2 · cómo se automatizan
s = slide("Cuatro tipos de prueba, todas automáticas", 2, "Nicolas: Una prueba automatizada es un programa que usa una parte del sistema y revisa que el resultado sea el esperado. Nadie hace clic: corren solas en cada push, y si una falla, el cambio no entra.")
kinds = [("Unitarias", "Una clase sola, en memoria. Milisegundos.", "JUnit 6", CILANTRO),
         ("Integración", "La app completa con PostgreSQL real en Docker.", "Testcontainers + MockMvc", PAPA),
         ("API E2E", "El sistema encendido, desde fuera, por HTTP.", "smoke_api.py", COBRE),
         ("Navegador E2E", "Un navegador real con dos personas.", "e2e_ui.py · Playwright", TOMATE)]
for k, (t1, t2, tool, c) in enumerate(kinds):
    x = 0.6 + k * 3.08
    card(s, x, 1.35, 2.85, 2.3)
    b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, i(x + 0.25), i(1.6), i(0.6), i(0.12)); b.fill.solid(); b.fill.fore_color.rgb = c; b.line.fill.background()
    text(s, x + 0.25, 1.85, 2.4, 1.7, [[(t1, True, TINTA)], [(t2, False, TINTA)], [(tool, True, PIEDRA)]], size=15)
pic(s, CI, 0.6, 3.95, 6.6, 2.85, "GitHub Actions corre todo en cada push")
text(s, 7.5, 4.0, 5.2, 2.8, [[("git push → GitHub Actions → mvn verify", True, COBRE)],
                              [("890 pruebas del backend en cada cambio", False, TINTA)],
                              [("JaCoCo: falla si la cobertura baja del 80 %", False, TINTA)],
                              [("Si algo falla, no hay merge ni despliegue", True, TINTA)],
                              [("Las dos E2E se corren contra el servidor encendido", False, PIEDRA)]], size=16)

# 3-6 · cada prueba
test_slide(3, "Unitarias: código de casa y solicitudes de permiso", "unit-code", "unit-res",
           "Prueban una sola clase en memoria, sin base de datos ni red.",
           ["JoinCodeTest: 8 caracteres sin O, 0, I ni 1; nunca da el rol de dueño",
            "AccessRequestTest: una solicitud se responde una sola vez; nadie se pide permiso a sí mismo",
            "NotificationChannelsTest: la respuesta le llega solo a quien pidió"],
           "12 pruebas, 0 fallos · BUILD SUCCESS en 3 s", CILANTRO,
           "Nicolas: Las unitarias prueban una clase sola, en memoria, y tardan milisegundos. Aquí, el código para unirse a una casa y las solicitudes de permiso. Resultado: doce de doce.")
test_slide(4, "Integración: la comida viaja con su dueño", "int-code", "int-res",
           "Arranca la app completa con un PostgreSQL 18 real en Docker (Testcontainers) y le hace peticiones con MockMvc.",
           ["Quien sale de una casa se lleva su comida; al unirse a otra entra a esa nevera",
            "Las latas llegan con 720 g, 360 g por unidad, y siguen privadas",
            "La leche llega con su fecha; el otro solo ve \"Alimento privado\""],
           "2 pruebas, 0 fallos · BUILD SUCCESS", CILANTRO,
           "Jenifer: La de integración levanta una base de datos real solo para la prueba y la borra al final. Cuenta una historia: Ana deja su casa, se une a la de Beto y su comida viaja con ella, igual de privada y con su fecha. Dos de dos.")
test_slide(5, "API de extremo a extremo: smoke_api.py", "api-code", "api-res",
           "Un script en Python que usa el sistema encendido, desde fuera, por HTTP, con tres personas.",
           ["Lo permitido responde bien y lo prohibido se rechaza (401, 403, 409)",
            "Una persona solo puede estar en una casa",
            "Cada notificación le llega solo a quien debe",
            "Hasta Gemini: aprende un alimento y el chef responde"],
           "147 de 147 comprobaciones OK", CILANTRO,
           "Jenifer: Este script usa la API como lo haría la app. No solo mira que responda: revisa las reglas, incluido lo que debe rechazarse. Ciento cuarenta y siete de ciento cuarenta y siete.")
test_slide(6, "Navegador de extremo a extremo: e2e_ui.py", "e2e-code", "e2e-res",
           "Playwright abre un navegador real y usa la app como dos personas.",
           ["Registro, casa, nevera y 2 latas por unidades",
            "Unirse con el código y pedir permiso",
            "La notificación le llega al dueño, aprueba y responde",
            "Cada pestaña carga, sin errores, al agrandar la pantalla y al cerrar sesión"],
           "29 de 32: 3 fallos = 2 defectos reales encontrados", TOMATE,
           "Juan: La de navegador hace el recorrido completo como un usuario. Dio veintinueve de treinta y dos: los tres fallos son defectos reales que encontró, que vemos en la siguiente.")

# 7 · defectos
s = slide("Lo que encontró la prueba de navegador, y el plan", 7, "Jenifer: Encontró dos defectos. No se corrigen en esta entrega porque solo se trabaja en el repositorio de documentación; quedaron como issues 46 y 47 del sprint 5, cada uno con su solución y la prueba que lo va a confirmar. Ninguno pierde datos ni deja pasar a nadie: eso lo confirma la prueba de la API.")
for k, (iss, t1, cause, plan) in enumerate([
        ("#46", "Notificaciones en inglés", "Las frases se guardaron en la tabla translations y el servidor traduce desde message_templates.", "Migración V91 que las mueve; prueba de integración en español; e2e_ui.py vuelve a pasar."),
        ("#47", "404 de /market-budget", "Sin presupuesto, la API responde 404 en vez de 204; la consola lo marca como error.", "Responder 204; actualizar smoke_api.py; e2e_ui.py sin errores de consola.")]):
    x = 0.6 + k * 6.15
    card(s, x, 1.35, 5.9, 4.0)
    text(s, x + 0.3, 1.5, 5.4, 3.8, [[(f"Issue {iss} · sprint 5", True, TOMATE)], [(t1, True, TINTA)], [("Por qué pasa", True, COBRE)], [(cause, False, TINTA)], [("Plan", True, COBRE)], [(plan, False, TINTA)]], size=16)
card(s, 0.6, 5.65, 12.05, 1.15, fill=MORA)
text(s, 0.9, 5.78, 11.5, 1.0, [[("No se corrigen aquí: la entrega solo edita el repositorio de documentación. ", True, PAPA), ("Se documentan, se registran en el tablero y se planean, con la prueba que confirmará la solución.", False, BLANCO)]], size=16)

# 8 · cómo correrlas y resumen
s = slide("Cómo se corren y qué dieron", 8, "Juan: Todo se corre desde VS Code, en Terminal, Run Task. Y estos son los resultados: las pruebas encontraron dos defectos que ya tienen plan.")
rows = [("Unitarias nuevas", "Unitarias nuevas", "12 / 12", CILANTRO), ("Integración", "Prueba 1 · Integración", "2 / 2", CILANTRO),
        ("API E2E", "Prueba 2 · API de extremo a extremo", "147 / 147", CILANTRO), ("Navegador E2E", "Prueba 3 · Navegador", "29 / 32", TOMATE),
        ("Suite completa", "Suite completa del backend", "890 pruebas", CILANTRO)]
tbl = s.shapes.add_table(len(rows) + 1, 3, i(0.6), i(1.35), i(12.1), i(4.2)).table
for j, (h, wd) in enumerate(zip(["Prueba", "Tarea de VS Code (Terminal → Run Task)", "Resultado"], [3.0, 6.6, 2.5])):
    tbl.columns[j].width = i(wd); c = tbl.cell(0, j); c.text = h; c.fill.solid(); c.fill.fore_color.rgb = TINTA
    r = c.text_frame.paragraphs[0].runs[0]; r.font.color.rgb = BLANCO; r.font.bold = True; r.font.size = Pt(16)
for k, (a, b, res, col) in enumerate(rows, 1):
    for j, v in enumerate([a, b, res]):
        c = tbl.cell(k, j); c.text = v; c.fill.solid(); c.fill.fore_color.rgb = CARTA if k % 2 else PAPEL
        r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(16); r.font.color.rgb = TINTA
        if j == 2:
            c.fill.fore_color.rgb = col; r.font.color.rgb = BLANCO; r.font.bold = True
text(s, 0.6, 5.85, 12.1, 1.0, [[("Todo está en el repositorio de documentación: ", True, TINTA), ("pruebas/README.md, scripts/qa/ y el plan de pruebas en Excel (31 casos).", False, TINTA)], [("¿Preguntas?", True, COBRE)]], size=17)

prs.save(OUT)
print("ok", len(prs.slides))
