"""Recorre la API de HayPaComer en local con cuentas temporales y comprueba códigos de estado.

Uso: python3 -I smoke_api.py [base]   (por defecto http://localhost:8090)
Crea tmp-a/b/c@local.test, una casa, una nevera y datos; al final borra la casa. Los usuarios
se borran aparte (no hay endpoint para eso).
"""

import json
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8090") + "/api/v1"
PW = "Prueba-1234-segura"
results = []


def call(method, path, body=None, tok=None, expect=200, label=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"content-type": "application/json"}
    if tok:
        headers["authorization"] = "Bearer " + tok
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            status, text = resp.status, resp.read()
    except urllib.error.HTTPError as error:
        status, text = error.code, error.read()
    except Exception as error:  # timeouts and the like
        status, text = 0, str(error).encode()
    expected = expect if isinstance(expect, (list, tuple, set)) else [expect]
    ok = status in expected
    results.append((ok, method, label or path, status, expected, text[:160].decode(errors="replace") if not ok else ""))
    if raw:
        return status, text
    try:
        return json.loads(text) if text else None
    except ValueError:
        return text


def login(email):
    call("POST", "/auth/register", {"email": email, "password": PW, "displayName": email.split("@")[0]}, expect=[201, 409], label="POST /auth/register " + email)
    session = call("POST", "/auth/login", {"email": email, "password": PW}, label="POST /auth/login")
    return session["accessToken"], session["refreshToken"]


A, A_REFRESH = login("tmp-a@local.test")
Bt, _ = login("tmp-b@local.test")
Ct, _ = login("tmp-c@local.test")

# --- public and account
call("GET", "/status", tok=A)
call("GET", "/i18n")
call("GET", "/i18n/es-CO")
call("GET", "/auth/demo", expect=[200, 404])
call("GET", "/fridge-examples", tok=A)
call("GET", "/settings/defaults", tok=A)
call("GET", "/recipe-templates", tok=A)
call("GET", "/foods?q=cerv", tok=A)
me_a = call("GET", "/me", tok=A)
call("PUT", "/me/locale", {"locale": "es-CO"}, tok=A, expect=[200, 204])
call("GET", "/me/notification-preferences", tok=A)
call("PUT", "/me/notification-preferences", {"channels": ["WEB"]}, tok=A, expect=[200, 204])
call("GET", "/notifications", tok=A)
call("POST", "/auth/refresh", {"refreshToken": A_REFRESH}, label="POST /auth/refresh")
call("GET", "/me", expect=401, label="GET /me sin sesión -> 401")
call("POST", "/auth/forgot-password", {"email": "tmp-a@local.test"}, expect=[200, 202, 204])

# --- households: one home per person, codes, same permissions
home = call("POST", "/households", {"name": "Prueba", "currency": "COP", "timezone": "America/Bogota"}, tok=A, expect=201)
H = home["id"]
P = f"/households/{H}"
call("POST", "/households", {"name": "Otra", "currency": "COP", "timezone": "America/Bogota"}, tok=A, expect=409, label="POST /households con casa -> 409")
call("GET", "/households", tok=A)
call("GET", P, tok=A)
code = call("GET", P + "/join-code", tok=A)["code"]
call("POST", "/households/join", {"code": "ZZZZ-ZZZZ"}, tok=Bt, expect=400, label="POST /households/join código falso -> 400")
call("POST", "/households/join", {"code": code.lower()}, tok=Bt, label="POST /households/join (minúsculas)")
call("POST", "/households/join", {"code": code}, tok=Bt, expect=409, label="POST /households/join repetido -> 409")
call("GET", P + "/join-code", tok=Bt, label="GET join-code como integrante")
call("PATCH", P, {"name": "Prueba renombrada"}, tok=Bt, label="PATCH casa como integrante")
call("POST", P + "/join-code", {}, tok=A, expect=201, label="POST join-code (nuevo, creador)")
code = call("GET", P + "/join-code", tok=A)["code"]
other = call("POST", "/households", {"name": "De C", "currency": "COP", "timezone": "America/Bogota"}, tok=Ct, expect=201)
call("POST", "/households/join", {"code": code}, tok=Ct, expect=409, label="join estando en otra casa -> 409")
call("DELETE", f"/households/{other['id']}", tok=Ct, expect=204, label="DELETE casa propia (C)")
call("POST", "/households/join", {"code": code}, tok=Ct, label="join tras eliminar su casa")
c_id = call("GET", "/me", tok=Ct)["id"]
b_id = call("GET", "/me", tok=Bt)["id"]
call("DELETE", f"{P}/members/{c_id}", tok=Bt, expect=403, label="integrante saca a otro -> 403")
call("DELETE", f"{P}/members/{c_id}", tok=A, expect=204, label="creador saca a C")
call("DELETE", P, tok=Bt, expect=403, label="integrante elimina casa -> 403")
call("GET", P + "/profiles", tok=A)
call("PUT", P + "/profile", {"diet": "OMNIVORE", "allergies": [], "avoidedFoods": []}, tok=Bt, expect=[200, 204])
call("GET", P + "/settings", tok=Bt)
call("PUT", P + "/settings", {"key": "food.at-risk-days", "value": "3"}, tok=Bt, expect=[200, 204], label="PUT settings como integrante")
call("GET", P + "/invitations", tok=A)
inv = call("POST", P + "/invitations", {"email": "tmp-z@local.test", "role": "MEMBER"}, tok=A, expect=201)
if isinstance(inv, dict):
    call("DELETE", f"{P}/invitations/{inv['id']}", tok=A, expect=204)

# --- fridge
fridge = call("POST", P + "/fridges", {"name": "Cocina", "layout": "STANDARD"}, tok=Bt, expect=201, label="POST fridges como integrante")
F = fridge["id"]
trays = []
def walk(node):
    if node.get("type") == "TRAY":
        trays.append(node["id"])
    for child in node.get("children", []):
        walk(child)
for f in call("GET", P + "/fridges", tok=A):
    walk(f)
call("GET", f"{P}/fridges/{F}/shape", tok=A)
call("PUT", f"{P}/fridges/{F}/shape", {"type": "SINGLE_DOOR", "shelves": 3, "doorRacks": 1, "drawers": 1, "freezerShelves": 0, "hinge": "LEFT", "widthCm": 55, "heightCm": 145, "depthCm": 60}, tok=Bt, expect=[200, 204], label="PUT shape como integrante")
trays = []
for f in call("GET", P + "/fridges", tok=A):
    walk(f)
call("GET", f"{P}/fridges/{F}/twin", tok=A)
call("GET", f"{P}/fridges/{F}/space", tok=A)
call("GET", f"{P}/fridges/{F}/session", tok=A, expect=[200, 204, 404])
call("GET", P + "/cold-chain", tok=A)
call("GET", f"{P}/cold-investigation?fridgeId={F}&hours=24", tok=A)
call("GET", P + "/expiry-estimate?food=Milk&zone=SHELF&opened=false", tok=A)
call("GET", P + "/foods/density?food=Milk", tok=A)
call("POST", "/foods/interpret", {"food": "Milk", "quantity": "1 l"}, tok=A)

# --- items: units, visibility, ask-first
T0, T1 = trays[0], trays[1]
cans = call("POST", P + "/items", {"fridgeId": F, "trayId": T0, "food": "Beer can", "grams": 720, "pieceGrams": 360, "visibility": "ASK_FIRST"}, tok=A, expect=201, label="POST items por unidades (2 latas, preguntar antes)")
milk = call("POST", P + "/items", {"fridgeId": F, "trayId": T0, "food": "Milk", "grams": 1000}, tok=A, expect=201)
priv = call("POST", P + "/items", {"fridgeId": F, "trayId": T1, "food": "Chorizo", "grams": 300, "visibility": "PRIVATE"}, tok=A, expect=201)
inv_b = call("GET", P + "/inventory", tok=Bt)
can_row = next((i for i in inv_b if i["id"] == cans["itemId"]), {})
results.append((can_row.get("pieceGrams") == 360 and round(can_row["grams"] / can_row["pieceGrams"]) == 2, "CHECK", "inventario: 2 latas con pieceGrams 360", can_row.get("pieceGrams"), [360], ""))
results.append((any(i["name"] == "Private food" for i in inv_b), "CHECK", "privado oculto para B", "", [], ""))
call("GET", P + "/inventory?rescueFirst=true", tok=A)
call("GET", P + "/kitchen", tok=A)
call("POST", f"{P}/items/{cans['itemId']}/consume", {"grams": 360}, tok=Bt, expect=403, label="consumir 'preguntar antes' sin permiso -> 403")
req = call("POST", f"{P}/items/{cans['itemId']}/access-requests", tok=Bt, expect=201, label="pedir permiso")
call("POST", f"{P}/items/{cans['itemId']}/access-requests", tok=Bt, expect=201, label="pedir permiso dos veces (misma solicitud)")
call("POST", f"{P}/access-requests/{req['id']}/approve", tok=Bt, expect=403, label="aprobar su propia solicitud -> 403")
listed = call("GET", P + "/access-requests", tok=A)
results.append((any(r["id"] == req["id"] and r["toAnswer"] for r in listed or []), "CHECK", "A ve la solicitud por responder", "", [], ""))
notes_a = call("GET", "/notifications", tok=A)
results.append((any(n.get("type") == "FOOD_REQUEST" for n in notes_a or []), "CHECK", "A recibe notificación de la solicitud", "", [], str([n.get("type") for n in notes_a or []])))
results.append((not any(n.get("type") == "FOOD_REQUEST" for n in call("GET", "/notifications", tok=Bt) or []), "CHECK", "B no recibe la notificación de A", "", [], ""))
call("POST", f"{P}/access-requests/{req['id']}/approve", tok=A, label="aprobar")
notes_b = call("GET", "/notifications", tok=Bt)
results.append((any(n.get("type") == "FOOD_REQUEST_ANSWERED" for n in notes_b or []), "CHECK", "B recibe notificación de la respuesta", "", [], str([n.get("type") for n in notes_b or []])))
call("POST", f"{P}/access-requests/{req['id']}/deny", tok=A, expect=409, label="responder dos veces -> 409")
call("POST", f"{P}/items/{cans['itemId']}/consume", {"grams": 360}, tok=Bt, label="consumir con permiso")
after = next((i for i in call("GET", P + "/inventory", tok=A) if i["id"] == cans["itemId"]), {})
results.append((after.get("grams") == 360 and round(after["grams"] / after["pieceGrams"]) == 1, "CHECK", "queda 1 lata tras consumir 1", after.get("grams"), [360], ""))
call("POST", f"{P}/items/{priv['itemId']}/consume", {"grams": 10}, tok=Bt, expect=403, label="consumir privado ajeno -> 403")
call("PUT", f"{P}/items/{priv['itemId']}/visibility", {"visibility": "SHARED"}, tok=Bt, expect=403, label="cambiar visibilidad ajena -> 403")
call("PUT", f"{P}/items/{priv['itemId']}/visibility", {"visibility": "ASK_FIRST"}, tok=A, label="cambiar visibilidad propia")
call("POST", f"{P}/items/{priv['itemId']}/grants", {"userId": b_id}, tok=A)
call("DELETE", f"{P}/items/{priv['itemId']}/grants/{b_id}", tok=A)
call("POST", f"{P}/items/{milk['itemId']}/open", tok=A)
call("POST", f"{P}/items/{milk['itemId']}/move", {"trayId": T1}, tok=Bt)
snap = call("POST", P + "/snapshots", {"reason": "antes"}, tok=A, expect=201)
call("GET", P + "/snapshots", tok=A)
call("POST", f"{P}/items/{milk['itemId']}/discard", tok=A)
call("POST", P + "/inventory/undo", tok=A)
if isinstance(snap, dict):
    call("POST", f"{P}/snapshots/{snap['id']}/restore", tok=Bt, label="restaurar snapshot como integrante")
call("GET", P + "/activity?limit=20", tok=A)

# --- market, money, analytics
call("GET", P + "/market-list", tok=A)
mi = call("POST", P + "/market-list/items", {"food": "Egg", "grams": 360}, tok=Bt, expect=201)
if isinstance(mi, dict) and mi.get("id"):
    call("PATCH", f"{P}/market-list/items/{mi['id']}", {"grams": 720}, tok=A)
    call("POST", f"{P}/market-list/items/{mi['id']}/check", tok=A, expect=[200, 204])
    call("DELETE", f"{P}/market-list/items/{mi['id']}/check", tok=A, expect=[200, 204])
    call("DELETE", f"{P}/market-list/items/{mi['id']}", tok=A, expect=[200, 204])
call("DELETE", P + "/market-list/checked", tok=A, expect=[200, 204])
call("GET", P + "/market-budget", tok=A, expect=404, label="GET market-budget sin presupuesto -> 404")
call("PUT", P + "/market-budget", {"monthly": 500000}, tok=Bt)
call("GET", P + "/market-budget", tok=A)
call("GET", P + "/prices", tok=A)
call("PUT", P + "/prices", {"food": "Milk", "pricePerKg": 4800}, tok=Bt, expect=[200, 204])
call("GET", P + "/analytics", tok=A)
call("GET", P + "/analytics/weekly-digest", tok=A)
status, _ = call("GET", P + "/analytics/report?format=CSV", tok=A, raw=True, expect=[200])

# --- recipes, planning, cooking
egg_recipe = {"name": "Huevos pericos", "servings": 2, "minutes": 10, "requirements": [{"food": "Egg", "grams": 110}], "steps": [{"instruction": "Batir y cocinar"}]}
call("GET", P + "/recipes", tok=A)
call("POST", P + "/recipes", egg_recipe, tok=A, expect=201)
call("POST", P + "/recipes/evaluate", {**{k: egg_recipe[k] for k in ("name", "servings", "minutes", "requirements")}, "targetServings": 2, "strategy": "FLEXIBLE"}, tok=A)
call("POST", P + "/recipes/missing-to-market", {**{k: egg_recipe[k] for k in ("name", "servings", "minutes", "requirements")}, "targetServings": 2}, tok=A, expect=[200, 201])
call("POST", P + "/suggestions", {"candidates": [egg_recipe], "servings": 2, "maxMinutes": 30, "limit": 3}, tok=A)
call("POST", P + "/rescue", {"candidates": [egg_recipe], "servings": 2, "maxMinutes": 30, "limit": 3}, tok=A)
plan = call("POST", P + "/weekly-plans", {"servings": 2}, tok=A, expect=[200, 201])
call("GET", P + "/weekly-plans/current", tok=A, expect=[200, 204, 404])
call("POST", P + "/market-list/from-plan", tok=A, expect=[200, 201, 404])
session = call("POST", P + "/cooking-sessions", {**egg_recipe, "targetServings": 2}, tok=A, expect=[200, 201])
call("GET", P + "/cooking-sessions/active", tok=A, expect=[200, 204])
if isinstance(session, dict) and session.get("id"):
    S = f"{P}/cooking-sessions/{session['id']}"
    call("GET", S, tok=A)
    call("POST", S + "/pause", tok=A, expect=409, label="pausar antes de empezar -> 409")
    call("POST", S + "/next", tok=A)
    call("POST", S + "/pause", tok=A)
    call("POST", S + "/resume", tok=A)
    call("GET", S + "/timer", tok=A, expect=[200, 204])
    call("POST", S + "/abandon", tok=A)

# --- devices (simulator)
dev = call("POST", P + "/devices", {"fridgeId": F, "name": "Sim", "kind": "SIMULATOR"}, tok=Bt, expect=201, label="POST devices como integrante")
call("GET", P + "/devices", tok=A)
if isinstance(dev, dict):
    key = dev.get("apiKey")
    req2 = urllib.request.Request(BASE + "/device/whoami", headers={"X-Device-Key": key} if key else {})
    try:
        with urllib.request.urlopen(req2, timeout=20) as resp:
            results.append((resp.status == 200, "GET", "/device/whoami con clave", resp.status, [200], ""))
    except urllib.error.HTTPError as error:
        results.append((False, "GET", "/device/whoami con clave", error.code, [200], error.read()[:120].decode()))
    call("DELETE", f"{P}/devices/{dev['device']['id']}", tok=A, expect=204)

# --- AI (Gemini)
learned = call("POST", P + "/foods", {"name": "Gaseosa Postobón en lata"}, tok=A, expect=[200, 201], label="IA: aprender alimento")
chat = call("POST", P + "/agent/chat", {"message": "¿Qué puedo cocinar hoy?"}, tok=A, label="IA: chat del chef")
call("GET", P + "/agent/conversations", tok=A)
call("GET", P + "/agent/memory", tok=A)

# --- leaving and deleting
call("DELETE", f"{P}/members/{b_id}", tok=Bt, expect=204, label="B sale de la casa")
call("GET", P, tok=Bt, expect=404, label="B ya no ve la casa")
call("DELETE", P, tok=A, expect=204, label="A elimina la casa")
call("GET", "/households", tok=A)
call("POST", "/auth/logout", {"refreshToken": A_REFRESH}, expect=[200, 204])

failed = [r for r in results if not r[0]]
for ok, method, label, status, expected, body in results:
    print(("OK  " if ok else "FAIL"), method, label, status, "" if ok else f"esperado {expected} {body}")
print(f"\n{len(results) - len(failed)}/{len(results)} OK")
learned_name = learned.get("name") if isinstance(learned, dict) else None
print("IA aprendió:", learned_name)
print("chef respondió:", (chat or {}).get("reply", (chat or {}).get("text", str(chat)[:100])) if isinstance(chat, dict) else chat)
