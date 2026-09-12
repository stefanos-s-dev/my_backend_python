from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# 1. Ενεργοποίηση CORS (Απαραίτητο για να επικοινωνεί το Flutter με την Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Επιτρέπει προσβάσεις από οποιαδήποτε συσκευή/browser
    allow_credentials=True,
    allow_methods=["*"], # Επιτρέπει GET, POST, PUT, DELETE
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn


# --- GET: Διάβασμα όλων των εγγραφών ---
@app.get("/people")
def get_people():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Παίρνουμε και το μοναδικό 'rowid' από την SQLite ως 'id'
    cursor.execute("SELECT rowid as id, * FROM people")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# --- POST: Προσθήκη νέου μέλους ---
@app.post("/people")
def create_person(person: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO people (ΟΝΟΜΑ, ΦΥΛΟ, ΕΚΚΛΗΣΙΑ, Σταθερό, Κινητό, `ΟΝΟΜΑ ΣΥΖΥΓΟΥ`, Email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        person.get("ΟΝΟΜΑ", ""),
        person.get("ΦΥΛΟ", ""),
        person.get("ΕΚΚΛΗΣΙΑ", ""),
        person.get("Σταθερό", ""),
        person.get("Κινητό", ""),
        person.get("ΟΝΟΜΑ ΣΥΖΥΓΟΥ", ""),
        person.get("Email", "")
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Η εγγραφή προστέθηκε επιτυχώς!", "id": new_id}


# --- PUT: Ενημέρωση/Επεξεργασία εγγραφής ---
@app.put("/people/{person_id}")
def update_person(person_id: int, person: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE people 
        SET ΟΝΟΜΑ=?, ΦΥΛΟ=?, ΕΚΚΛΗΣΙΑ=?, Σταθερό=?, Κινητό=?, `ΟΝΟΜΑ ΣΥΖΥΓΟΥ`=?, Email=?
        WHERE rowid=?
    """, (
        person.get("ΟΝΟΜΑ", ""),
        person.get("ΦΥΛΟ", ""),
        person.get("ΕΚΚΛΗΣΙΑ", ""),
        person.get("Σταθερό", ""),
        person.get("Κινητό", ""),
        person.get("ΟΝΟΜΑ ΣΥΖΥΓΟΥ", ""),
        person.get("Email", ""),
        person_id
    ))
    conn.commit()
    conn.close()
    return {"message": f"Η εγγραφή {person_id} ενημερώθηκε!"}


# --- DELETE: Διαγραφή εγγραφής ---
@app.delete("/people/{person_id}")
def delete_person(person_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM people WHERE rowid = ?", (person_id,))
    conn.commit()
    conn.close()
    return {"message": f"Η εγγραφή {person_id} διαγράφηκε!"}