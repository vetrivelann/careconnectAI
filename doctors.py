from database import connect_db

print("running doctors script......")
conn = connect_db()
cursor = conn.cursor()

doctors = [
    ("1", "Dr. Arjun", "Dermatologist", 4.5),
    ("2", "Dr. Meena", "Dermatologist", 4.8),

    ("3", "Dr. Ravi", "Cardiologist", 4.7),
    ("4", "Dr. Suresh", "Cardiologist", 4.6),

    ("5", "Dr. Priya", "Neurologist", 4.9),
    ("6", "Dr. Karthik", "Neurologist", 4.4),

    ("7", "Dr. Lakshmi", "Ophthalmologist", 4.7),
    ("8", "Dr. John", "Ophthalmologist", 4.5),

    ("9", "Dr. Anitha", "ENT Specialist", 4.6),
    ("10", "Dr. Manoj", "ENT Specialist", 4.3),

    ("11", "Dr. Kumar", "Orthopedic", 4.6),
    ("12", "Dr. Raj", "Orthopedic", 4.4),

    ("13", "Dr. Deepa", "Gastroenterologist", 4.8),
    ("14", "Dr. Vikram", "Gastroenterologist", 4.5),

    ("15", "Dr. Nisha", "Nephrologist", 4.7),
    ("16", "Dr. Harish", "Nephrologist", 4.4),

    ("17", "Dr. Sanjay", "Hepatologist", 4.6),
    ("18", "Dr. Kavya", "Hepatologist", 4.7),

    ("19", "Dr. Rahul", "Psychiatrist", 4.5),
    ("20", "Dr. Sneha", "Psychiatrist", 4.8),

    ("21", "Dr. General1", "General Physician", 4.5),
    ("22", "Dr. General2", "General Physician", 4.6),
]

for d in doctors:
    cursor.execute("INSERT INTO doctors VALUES (%s,%s,%s,%s)", d)

conn.commit()
conn.close()

print("Doctors added!")