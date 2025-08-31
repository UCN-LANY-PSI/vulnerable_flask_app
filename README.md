# Kontrolleret SQL-injektion og forebyggelse

## Formål
-	Udføre et kontrolleret SQL-injektionsangreb i et testmiljø for at forstå mekanismen.
-	Refaktorere sårbar kode til parameteriserede forespørgsler.
-	Sammenligne resultater før/efter sikkerhedsforbedring.
-	Oprette en lille testdatabase med data.

## Forudsætninger
- Python 3.10+
-	Flask (installer: pip install flask)
-	Ingen ekstern database krævet (SQLite følger med Python)

## Etik og rammer
-	Øvelsen udføres kun på eget, lokalt testmiljø.
-	Brug ikke teknikkerne mod systemer, du ikke har rettighed til at teste.

## Oversigt over dele
1.	Opret testdatabase og data  
1.	Kør en bevidst sårbar mini-webapp (Flask)  
1.	Udfør SQL-injektion og observer effekten  
1.	Refaktorér til parameteriserede forespørgsler  
1.	Sammenlign før/efter og skriv kort konklusion  

### 1. Opret testdatabase og data

**Formål**  

At oprette en lokal SQLite-database (test.db) med tabellen users og realistiske rækker, så den kan bruges af app_vuln.py og app_secure.py.
Arbejdsgang

1. **Åbn filen setup_db_student.py**
   
   Læs kommentarfeltet øverst og gennemgå TODO 1–3.
  	
2. **Udfyld TODO 1 – USERS_SCHEMA**

   Opret tabellen users med præcis disse kolonner og krav:
   - id = INTEGER PRIMARY KEY AUTOINCREMENT
   - username = TEXT NOT NULL UNIQUE
   - email = TEXT NOT NULL
   - role = TEXT NOT NULL

   (gerne med CHECK(role IN ('user','manager','admin')))

   Kolonnenavne og typer skal matche ovenstående, ellers fejler sanity check.

3. **Udfyld TODO 2 – USERS_ROWS**

   Indsæt mindst 5 rækker som 3-tupler: (username, email, role).

   Krav:
   - Mindst én række med role='admin'.
   - Unikke username-værdier (ingen dubletter).
   - Brug realistiske værdier (fx alice, bob, …).

4. **(Valgfrit) Udfyld TODO 3 – USERS_INDEX_SQL**
   
   Opret eventuelt et indeks på username, fx:

   ```sql
   CREATE INDEX idx_users_username ON users(username);
   ```
   
5. **Kør scriptet**

   Første gang (eller når du vil starte forfra):

   ```bash
   python setup_db_student.py --fresh
   ```

   Uden --fresh overskrives ikke automatisk en eksisterende test.db.

6. **Forventet output**

   Hvis alt er korrekt, ser du:
   - Sanity check: OK
   - OK: test.db klar.

   Hvis noget mangler, får du en forklarende fejl (læs den og ret i filen):
   - NotImplementedError → USERS_SCHEMA indeholder stadig TODO-tekst.
   - Manglende kolonner/typer → ret USERS_SCHEMA.
   - For få rækker / ingen admin → tilføj i USERS_ROWS.
   - Dublerede usernames → ret værdierne i USERS_ROWS.

7. **Verificér databasen (valgfrit, men anbefalet)**

   Via SQLite-CLI:

   ```bash
   sqlite3 test.db
   .tables
   .schema users
   SELECT COUNT(*) FROM users;
   SELECT * FROM users LIMIT 5;
   .quit
   ```
   
   Tjek at tabellen users findes, og at der er mindst 5 rækker.

8. **Brug databasen i øvelsen**

   Når test.db er klar, kan du køre:

   python app_vuln.py

   ... og senere ...

   python app_secure.py

   **Acceptkriterier**
   - test.db oprettes i projektmappen.
   - Tabellens schema er: users(id, username, email, role) med krav som angivet.
   - Mindst 5 rækker i users, inkl. mindst én admin.
   - Sanity check: OK og ingen dubletter i username.
   - (Valgfrit) Indeks på username oprettet uden fejl.

---

B.	Sårbar mini-webapp med Flask
Kopier filen app_vuln.py (med bevidst sårbar forespørgsel):
Kør:
python app_vuln.py
Åbn i browser: http://127.0.0.1:5000/
Test normal forespørgsel: skriv alice i feltet.
C.	Udfør SQL-injektion
1.	I feltet, skriv: x' OR '1'='1
Tryk Søg.
Forvent: Appen returnerer mange rækker (alle brugere), selvom der blev søgt på “x…”.
Forklaring: WHERE username = 'x' OR '1'='1' gør betingelsen altid er sand.
2.	Prøv også en “lukning” og kommentering (afhænger af DB-dialekt): ' OR 1=1 –
Hvis du bruger URL’en direkte, så husk URL-encoding af mellemrum mm., men formularen ovenfor gør det nemt.
Observationer at notere:
•	Hvad returneres ved almindelig søgning vs. injektion?
•	Hvilken SQL blev logget i terminalen?
D.	Forebyggelse: parameteriserede forespørgsler
Målet
Gør den sårbare app sikker ved at kopiere koden og erstatte strengsammenkædning med parameteriserede forespørgsler + enkel inputkontrol.
Arbejdsgang
1.	Lav en kopi af den usikre fil app_vuln.py 
cp app_vuln.py app_secure.py
Åbn app_secure.py. Behold samme routes (/ og /search), men ret teksten i HTML-titlen til fx “(sikker)”.
2.	Find den sårbare del
I handleren for /search ligger der typisk:
name = request.args.get("name", "")
query = f"SELECT id, username, email, role FROM users WHERE username = '{name}'"
cur.execute(query)
Det er denne del, der skal refaktoreres.
3.	Tilføj enkel inputkontrol
Lige efter du henter name:
name = request.args.get("name", "").strip()
if len(name) > 50:
    return jsonify({"error": "Input for langt"}), 400
(Begrænsninger hjælper robustheden, men erstatter ikke parameterisering.)
4.	Erstat strengsammenkædning med parametre
Brug SQLite-placeholders (?) og send værdier som anden parameter til execute:
query = "SELECT id, username, email, role FROM users WHERE username = ?"
cur.execute(query, (name,))
rows = cur.fetchall()
Tip: brug gerne context manager for at sikre lukning:
with sqlite3.connect(DB_PATH) as conn:
   cur = conn.cursor()
   cur.execute(query, (name,))
   rows = cur.fetchall()
5.	(Valgfrit) Sikkert delvist match (LIKE)
Hvis du vil understøtte søgning på dele af navnet:
query = "SELECT id, username, email, role FROM users WHERE username LIKE '%' || ? || '%'"
cur.execute(query, (name,))
Her er stadig parameterisering – % tilføjes i SQL via streng-konkatenering, men inputtet er bundet som parameter.
6.	Fejlbeskeder og logging
Pak DB-kald ind i try/except, returnér generiske fejl til klienten, og log detaljer i serverkonsollen (ingen rå SQL-fejl til bruger):
try:
    # DB-kald
except Exception as e:
    print("Intern fejl:", e)
    return jsonify({"error": "Internal server error"}), 500
7.	Retest med samme input som før
o	Normal søgning: alice → forvent præcist match.
o	Injektion: x' OR '1'='1 → forvent ingen massivt datalæk (typisk tomt resultat).
o	Notér forskel i adfærd mellem app_vuln.py og app_secure.py.
8.	Dokumentér kort (5–8 linjer)
o	Hvad ændrede I i koden?
o	Hvordan ændrede resultatet sig (før/efter)?
o	Hvilke CIA-principper blev bedre beskyttet?
o	Hvad ville næste lag være (validering, least privilege, sikre fejl, logging)?
Acceptkriterier
•	Koden i app_secure.py bruger parameteriserede forespørgsler i alle DB-kald.
•	Enkel inputkontrol (trim, længdecheck) er tilføjet.
•	Ingen rå DB-fejl sendes til bruger.
•	Samme injektionsinput giver ikke datalæk i app_secure.py.
•	Kort sammenligning mellem sårbar og sikker version er skrevet.
E.	Sammenlign før/efter og konkludér
Skriv en kort sammenligning (5–8 linjer):
•	Hvad skete i den sårbare version ved injektion?
•	Hvad skete i den sikre version?
•	Hvilke CIA-principper berøres af den sårbare adfærd?
•	Hvilke kodeændringer gjorde forskellen (parameterisering, evt. længdecheck)?
•	Hvad ville være næste lag i defense-in-depth (fx least privilege, generiske fejlbeskeder, logging/monitorering)?

