from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sqlite3
import pandas as pd

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


def init_shift_templates_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shift_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_shift_templates_table()


@app.get("/publishers")
def get_publishers():
    xlsx_files = list(Path(".").glob("*.xlsx"))
    if not xlsx_files:
        return {"publishers": []}
    file_path = xlsx_files[0]

    try:
        publishers_column = pd.read_excel(file_path, usecols=[0]).iloc[:, 0]
    except (OSError, ValueError, ImportError):
        return {"publishers": []}

    publishers = [
        str(value).strip()
        for value in publishers_column.dropna()
        if str(value).strip()
    ]
    return {"publishers": publishers}


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


@app.get("/shift-templates")
def get_shift_templates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rowid as id, * FROM shift_templates ORDER BY day_of_week, start_time")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/shift-templates")
def create_shift_template(template: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO shift_templates (day_of_week, start_time, end_time)
        VALUES (?, ?, ?)
    """, (
        template.get("day_of_week", ""),
        template.get("start_time", ""),
        template.get("end_time", "")
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Η εγγραφή προστέθηκε επιτυχώς!", "id": new_id}


@app.delete("/shift-templates/{template_id}")
def delete_shift_template(template_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shift_templates WHERE rowid = ?", (template_id,))
    conn.commit()
    conn.close()
    return {"message": f"Η εγγραφή {template_id} διαγράφηκε!"}


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