import psycopg2

# 🔥 CHANGE THESE VALUES (YOUR DETAILS)
DB_NAME = "healthcare"
DB_USER = "postgres"
DB_PASSWORD = "vetrisai@0109" 
DB_HOST = "localhost"
DB_PORT = "5432"


# =========================
# 🔗 CONNECT DATABASE
# =========================
def connect_db():
    return psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


# =========================
# 🗄️ CREATE TABLES
# =========================
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        role TEXT
    )
    """)

    # APPOINTMENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id TEXT PRIMARY KEY,
        name TEXT,
        date TEXT,
        time TEXT,
        doctor_type TEXT
    )
    """)

    # VITALS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vitals (
        vital_id TEXT PRIMARY KEY,
        patient_name TEXT,
        temperature REAL,
        blood_pressure TEXT,
        pulse INTEGER,
        recorded_at TEXT
    )
    """)

    # PRESCRIPTIONS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        prescription_id TEXT PRIMARY KEY,
        patient_name TEXT,
        doctor_name TEXT,
        medicine TEXT,
        dosage TEXT,
        notes TEXT,
        date TEXT
    )
    """)

    # DISCHARGE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discharge (
        discharge_id TEXT PRIMARY KEY,
        patient_name TEXT,
        doctor_name TEXT,
        summary TEXT,
        date TEXT
    )
    """)

    # REPORTS (OCR)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        report_id TEXT PRIMARY KEY,
        patient_name TEXT,
        file_name TEXT,
        extracted_text TEXT,
        date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
    doctor_id TEXT PRIMARY KEY,
    name TEXT,
    specialization TEXT,
    rating REAL
    )
    """)

    conn.commit()
    conn.close()


# RUN ONCE
create_tables()
print("PostgreSQL Database Connected & Tables Created!")