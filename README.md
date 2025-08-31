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
