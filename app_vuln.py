# app_vuln.py
# Sårbar Flask-app med SQL bygget via strengsammenkædning (DEMO – do not use in prod).

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "test.db"

HTML_FORM = """
<!doctype html>
<title>Brugeropslag (sårbar demo)</title>
<h1>Opslag efter username (sårbar)</h1>
<form method="get" action="/search">
  <input name="name" placeholder="fx alice">
  <button type="submit">Søg</button>
</form>
<p>Tip: Prøv input: x' OR '1'='1</p>
"""

@app.route("/")
def index():
    return HTML_FORM

@app.route("/search")
def search():
    name = request.args.get("name", "")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # BEVIDST SÅRBAR: string-konkatenering af brugerinput
    query = f"SELECT id, username, email, role FROM users WHERE username = '{name}'"
    print("Kører SQL (sårbar):", query)  # til undervisningsbrug

    try:
        cur.execute(query)
        rows = cur.fetchall()
    finally:
        conn.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)
