"""Prueba de punta a punta en el navegador (Playwright) con dos personas que comparten una casa.

Uso: python3 -I e2e_ui.py <chrome> <carpeta-capturas> [base]
Crea e2e-uno/e2e-dos@local.test (se borran luego por SQL).
"""

import sys
import time

from playwright.sync_api import sync_playwright

CHROME, SHOTS = sys.argv[1], sys.argv[2]
BASE = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8090"
PW = "Prueba-1234-segura"
results = []


def check(ok, label, extra=""):
    results.append((bool(ok), label, extra))


def page_for(browser, width=1280, height=900):
    page = browser.new_page(viewport={"width": width, "height": height}, locale="es-CO")
    page.errors = []
    page.on("pageerror", lambda error: page.errors.append(str(error)))
    page.on("console", lambda message: message.type == "error" and "favicon" not in message.text and page.errors.append(message.text))
    return page


def register(page, email, name):
    page.goto(BASE + "/#/register")
    page.wait_for_selector("input[name=displayName]", timeout=20000)
    page.fill("input[name=displayName]", name)
    page.fill("input[name=email]", email)
    page.fill("input[name=password]", PW)
    page.click("form button[type=submit]")
    page.wait_for_timeout(2500)
    if page.locator("input[name=password]").count():  # registered, now sign in
        page.goto(BASE + "/#/signin")
        page.wait_for_selector("input[name=email]")
        page.fill("input[name=email]", email)
        page.fill("input[name=password]", PW)
        page.click("form button[type=submit]")
    page.wait_for_selector("form [name=name], nav.tabs:not([hidden])", timeout=20000)


def go(page, route, wait=2500):
    page.goto(f"{BASE}/#/{route}")
    page.wait_for_timeout(wait)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])

    # --- landing and sign-in
    visitor = page_for(browser)
    visitor.goto(BASE + "/")
    visitor.wait_for_timeout(2500)
    check(visitor.locator("input[name=password]").count() == 0, "la raíz muestra la landing")
    visitor.goto(BASE + "/#/signin")
    visitor.wait_for_selector("[data-demo]", timeout=15000)
    check(visitor.locator("[data-demo]").count() >= 1, "botones de cuenta de prueba", str(visitor.locator("[data-demo]").all_text_contents()))
    visitor.close()

    # --- person one: registers, makes a home and its fridge
    uno = page_for(browser)
    register(uno, "e2e-uno@local.test", "Uno")
    uno.wait_for_selector("form [name=name]", timeout=20000)
    check(uno.locator("[data-join-home]").count() == 1, "alta ofrece crear o unirse con código")
    uno.fill("form [name=name]", "Casa E2E")
    uno.locator("form button[type=submit]").first.click()
    uno.wait_for_selector("nav.tabs:not([hidden])", timeout=20000)
    go(uno, "fridge")
    uno.wait_for_selector("[data-setup]", timeout=15000)
    uno.click("[data-setup] button[type=submit]")
    uno.wait_for_selector("[data-add-food]", timeout=20000)
    uno.keyboard.press("Escape")
    uno.wait_for_timeout(800)
    for dialog in uno.locator("dialog[open]").all():
        uno.keyboard.press("Escape")
    check(True, "nevera configurada")

    # add 2 cans by units, ask first
    go(uno, "fridge")
    uno.click("[data-add-food]")
    uno.wait_for_selector("[data-food-search]")
    chips = uno.locator("[data-chip] input[name=food]").count()
    check(chips >= 70, "el panel de agregar lista todo el catálogo", str(chips))
    uno.fill("[data-food-search]", "tomate")
    uno.wait_for_timeout(400)
    check(uno.locator("label.chip:has(input[value='Tomato'])").is_visible(), "buscar 'tomate' muestra Tomate")
    uno.fill("[data-food-search]", "lata")
    uno.wait_for_timeout(400)
    uno.locator("label.chip:has(input[value='Beer can'])").click()
    uno.click("[data-step-next]")
    uno.wait_for_timeout(400)
    check(uno.eval_on_selector("[name=unit]:checked", "e => e.value") == "u", "lata abre en unidades")
    uno.fill("input.grams[name=grams]", "2")
    uno.click("[data-step-next]")
    uno.wait_for_timeout(400)
    uno.locator("label.chip:has(input[name=visibility][value=ASK_FIRST])").click()
    while uno.locator("[data-step-next]").is_visible():
        uno.click("[data-step-next]")
        uno.wait_for_timeout(300)
    uno.click(".add-food button[type=submit]")
    uno.wait_for_timeout(3000)
    row = uno.locator(".food-row .value").first.text_content() or ""
    check("2 u." in row, "fila muestra 2 unidades", row)

    # home tab: rename and code
    go(uno, "home")
    uno.wait_for_selector("[data-code]", timeout=15000)
    code = (uno.text_content("[data-code]") or "").strip()
    check(len(code) == 9, "código de casa visible", code)
    uno.fill("[data-rename] [name=name]", "Casa E2E renombrada")
    uno.click("[data-rename] button")
    uno.wait_for_timeout(1500)
    check("renombrada" in (uno.text_content("[data-household]") or ""), "renombrar actualiza el encabezado")
    check(uno.locator("[data-delete-home]").count() == 1, "creador ve Eliminar casa")
    check(uno.locator("[data-create-home] input[disabled]").count() == 1, "crear bloqueado estando en una casa")

    # --- person two: registers and joins with the code
    dos = page_for(browser)
    register(dos, "e2e-dos@local.test", "Dos")
    dos.wait_for_selector("[data-join-home]", timeout=20000)
    dos.fill("[data-join-home] [name=code]", code.lower())
    dos.click("[data-join-home] button[type=submit]")
    dos.wait_for_selector("nav.tabs:not([hidden])", timeout=20000)
    go(dos, "home")
    dos.wait_for_selector("[data-code]", timeout=15000)
    check(dos.locator("[data-leave-home]").count() == 1, "integrante ve Salir de la casa")
    check(dos.locator("[data-remove]").count() == 0, "integrante no puede sacar a nadie")

    # asks for the cans
    go(dos, "fridge", 3500)
    ask = dos.locator("[data-ask]")
    check(ask.count() == 1, "integrante ve Pedir permiso")
    if ask.count():
        ask.first.click()
        dos.wait_for_timeout(2000)
        check(dos.locator("[data-ask]").count() == 0, "tras pedir, queda esperando")

    # owner: notification + approve
    go(uno, "fridge", 3500)
    badge = uno.locator("[data-inbox-count]")
    check(badge.is_visible(), "campana con aviso para el dueño", badge.text_content() or "")
    uno.click("[data-inbox]")
    uno.wait_for_timeout(1500)
    inbox = uno.locator(".inbox-sheet").text_content() or ""
    check("Solicitud de comida" in inbox and "pidió permiso" in inbox, "la notificación dice quién pidió", inbox[:160])
    uno.screenshot(path=f"{SHOTS}/e2e-notificacion-dueno.png")
    uno.keyboard.press("Escape")
    uno.wait_for_timeout(500)
    approve = uno.locator("[data-approve]")
    check(approve.count() == 1, "dueño ve Permitir en la nevera")
    if approve.count():
        approve.first.click()
        uno.wait_for_timeout(2000)

    # requester: notification of the answer, can use the cans now
    go(dos, "fridge", 3500)
    dos.click("[data-inbox]")
    dos.wait_for_timeout(1500)
    inbox = dos.locator(".inbox-sheet").text_content() or ""
    check("Respuesta a tu solicitud" in inbox and "te dejó usar" in inbox, "quien pidió recibe la respuesta", inbox[:160])
    dos.screenshot(path=f"{SHOTS}/e2e-notificacion-respuesta.png")
    dos.keyboard.press("Escape")

    # every tab loads without errors
    for route in ["now", "fridge", "market", "numbers", "chef", "home", "settings"]:
        go(uno, route, 3000)
        check(uno.locator("main h1").count() >= 1, f"pestaña {route} carga")
    check(not uno.errors, "sin errores de consola (uno)", "; ".join(uno.errors[:3]))
    check(not dos.errors, "sin errores de consola (dos)", "; ".join(dos.errors[:3]))

    # phone to full screen without reloading
    small = page_for(browser, 390, 844)
    small.goto(BASE + "/#/signin")
    small.wait_for_selector("input[name=email]")
    small.fill("input[name=email]", "e2e-uno@local.test")
    small.fill("input[name=password]", PW)
    small.click("form button[type=submit]")
    small.wait_for_selector("nav.tabs:not([hidden])", timeout=20000)
    go(small, "fridge", 3000)
    small.set_viewport_size({"width": 1280, "height": 800})
    small.wait_for_timeout(3000)
    check(small.locator("canvas.stage-canvas").count() == 1, "al agrandar aparece la cocina 3D sin recargar")
    overflow = small.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1")
    check(not overflow, "sin desborde horizontal tras agrandar")
    small.close()

    # sign out goes to the sign-in
    uno.evaluate("document.querySelector('[data-signout]').click()")
    uno.wait_for_timeout(2000)
    check(uno.locator("input[name=password]").count() == 1 and "signin" in uno.url, "cerrar sesión lleva al login", uno.url)
    browser.close()

for ok, label, extra in results:
    print(("OK  " if ok else "FAIL"), label, "" if ok else extra)
print(f"\n{sum(1 for r in results if r[0])}/{len(results)} OK")
