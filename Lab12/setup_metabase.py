"""Konfiguruje Metabase przez REST API: admin, polaczenie z baza, pytania, dashboard."""
import json, time, uuid, sys
import requests

BASE = "http://localhost:3000"
ADMIN = {"first_name": "BI", "last_name": "Admin", "email": "admin@ntpd.local", "password": "Ntpd!2026Bi"}

s = requests.Session()

def api(method, path, **kw):
    r = s.request(method, BASE + path, **kw)
    if not r.ok:
        print("ERR", method, path, r.status_code, r.text[:500]); r.raise_for_status()
    return r.json() if r.text else {}

# 1. setup -> admin + sesja
props = api("GET", "/api/session/properties")
token = props["setup-token"]
res = api("POST", "/api/setup", json={
    "token": token,
    "user": ADMIN,
    "prefs": {"site_name": "NTPD BI", "allow_tracking": False},
})
sess = res["id"]
s.headers.update({"X-Metabase-Session": sess})
print("admin+sesja OK")

# 2. polaczenie z PostgreSQL
db = api("POST", "/api/database", json={
    "name": "NTPD Hurtownia (PostgreSQL)",
    "engine": "postgres",
    "details": {"host": "postgres", "port": 5432, "dbname": "ntpd", "user": "bi", "password": "bi", "ssl": False},
})
db_id = db["id"]
print("baza dodana, id=", db_id)

# 3. sync + czekanie na metadane tabeli transactions
api("POST", f"/api/database/{db_id}/sync_schema")
table_id = None; fields = {}
for _ in range(40):
    meta = api("GET", f"/api/database/{db_id}/metadata")
    for t in meta.get("tables", []):
        if t["name"] == "transactions":
            table_id = t["id"]
            fields = {f["name"]: f["id"] for f in t.get("fields", [])}
    if table_id and {"status", "category", "amount", "event_time"} <= set(fields):
        break
    time.sleep(2)
assert table_id, "brak tabeli transactions po sync"
print("tabela transactions id=", table_id, "pola=", fields)

f_status, f_cat, f_amt, f_time = fields["status"], fields["category"], fields["amount"], fields["event_time"]

def card(name, dq, display, viz=None):
    payload = {"name": name, "dataset_query": dq, "display": display,
               "visualization_settings": viz or {}}
    c = api("POST", "/api/card", json=payload)
    print(f"  pytanie '{name}' id={c['id']} ({display})")
    return c["id"]

def mbql(query):
    return {"type": "query", "database": db_id, "query": query}

def native(sql, tags=None):
    return {"type": "native", "database": db_id,
            "native": {"query": sql, "template-tags": tags or {}}}

# field-filter template tag (do podpiecia filtra dashboardu do natywnego SQL)
def cat_tag():
    tid = str(uuid.uuid4())
    return {"category_filter": {"id": tid, "name": "category_filter",
            "display-name": "Category", "type": "dimension",
            "dimension": ["field", f_cat, None], "widget-type": "string/=", "default": None}}

cards = {}

# 3.1 kreator wizualny: liczba transakcji wg statusu -> pie
cards["pie_status"] = card("3.1 Transakcje wg statusu",
    mbql({"source-table": table_id, "aggregation": [["count"]],
          "breakout": [["field", f_status, None]]}), "pie")

# 3.2 agregacja wg kategorii: count + sum(amount) -> bar
cards["bar_category"] = card("3.2 Liczba i wartosc wg kategorii",
    mbql({"source-table": table_id,
          "aggregation": [["count"], ["sum", ["field", f_amt, None]]],
          "breakout": [["field", f_cat, None]]}), "bar")

# 3.3 SQL: przychod wg kategorii (paid) -> table (z field-filter dla dashboardu)
sql_rev = ("SELECT category, COUNT(*) AS events, ROUND(SUM(amount)::numeric,2) AS revenue\n"
           "FROM transactions\nWHERE status='paid' [[AND {{category_filter}}]]\n"
           "GROUP BY category ORDER BY revenue DESC")
cards["sql_revenue"] = card("3.3 Przychod wg kategorii (SQL)", native(sql_rev, cat_tag()), "table")

# Trend przychodu po minucie -> line
sql_trend = ("SELECT date_trunc('minute', event_time) AS minute,\n"
             "       ROUND(SUM(amount)::numeric,2) AS revenue\n"
             "FROM transactions\nWHERE status='paid' [[AND {{category_filter}}]]\n"
             "GROUP BY 1 ORDER BY 1")
cards["trend"] = card("Trend przychodu w czasie (po minucie)", native(sql_trend, cat_tag()), "line")

# KPI scalary
cards["kpi_revenue"] = card("KPI: Laczny przychod (paid)",
    native("SELECT ROUND(SUM(amount)::numeric,2) FROM transactions WHERE status='paid' [[AND {{category_filter}}]]", cat_tag()),
    "scalar")
cards["kpi_avg"] = card("KPI: Srednia wartosc transakcji (paid)",
    native("SELECT ROUND(AVG(amount)::numeric,2) FROM transactions WHERE status='paid' [[AND {{category_filter}}]]", cat_tag()),
    "scalar")

# Podglad tabeli (do zad.2) -> table
cards["preview"] = card("Podglad tabeli transactions",
    mbql({"source-table": table_id, "limit": 20}), "table")

# 4. dashboard z filtrem category
dash = api("POST", "/api/dashboard", json={"name": "Sprzedaz - przeglad (LAB12)"})
dash_id = dash["id"]
param_id = "cat_param"
cards_layout = [
    ("kpi_revenue", 0, 0, 6, 4), ("kpi_avg", 6, 0, 6, 4),
    ("bar_category", 0, 4, 12, 6), ("pie_status", 12, 4, 8, 6),
    ("trend", 0, 10, 12, 6), ("sql_revenue", 12, 10, 8, 6),
]
dashcards = []
for i, (key, x, y, w, h) in enumerate(cards_layout):
    cid = cards[key]
    # mapowanie filtra: natywne -> template-tag, MBQL -> field
    if key in ("sql_revenue", "trend", "kpi_revenue", "kpi_avg"):
        target = ["dimension", ["template-tag", "category_filter"]]
    elif key in ("bar_category", "pie_status", "preview"):
        target = ["dimension", ["field", f_cat, None]]
    else:
        target = None
    pm = [{"parameter_id": param_id, "card_id": cid, "target": target}] if target else []
    dashcards.append({"id": -(i + 1), "card_id": cid, "row": y, "col": x,
                      "size_x": w, "size_y": h, "parameter_mappings": pm,
                      "visualization_settings": {}})

api("PUT", f"/api/dashboard/{dash_id}", json={
    "dashcards": dashcards,
    "parameters": [{"id": param_id, "name": "Kategoria", "slug": "category",
                    "type": "string/=", "sectionId": "string"}],
})
print("dashboard id=", dash_id, "z filtrem 'Kategoria' i", len(dashcards), "kartami")

# 5. publiczny link do dashboardu (udostepnianie)
api("PUT", "/api/setting/enable-public-sharing", json={"value": True})
pub = api("POST", f"/api/dashboard/{dash_id}/public_link")
public_uuid = pub.get("uuid")
print("public dashboard uuid=", public_uuid)

out = {"session": sess, "db_id": db_id, "table_id": table_id,
       "cards": cards, "dash_id": dash_id, "public_uuid": public_uuid,
       "admin": ADMIN}
with open("mb_state.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nZAPISANO mb_state.json")
