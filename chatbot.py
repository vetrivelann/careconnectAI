import requests
import re


# =========================
# 🚨 EMERGENCY CHECK (BP)
# =========================
def check_emergency(user_input):
    match = re.search(r'(\d{2,3})/(\d{2,3})', user_input)
    if match:
        systolic = int(match.group(1))
        diastolic = int(match.group(2))
        if systolic >= 140 or diastolic >= 90:
            return True
    return False


# =========================
# 👨‍⚕️ DOCTOR SUGGESTION (SPECIALIZATION)
# =========================
def suggest_doctor(user_input):
    text = user_input.lower()

    # SKIN
    if any(x in text for x in ["skin", "rash", "itch", "pimple", "acne"]):
        return "Dermatologist"

    # HEART
    elif any(x in text for x in ["heart", "chest pain", "bp", "pressure"]):
        return "Cardiologist"

    # ORTHOPEDIC (VERY IMPORTANT)
    elif any(x in text for x in ["back", "back pain", "joint", "knee", "bone", "shoulder"]):
        return "Orthopedic"

    # EYE
    elif any(x in text for x in ["eye", "vision", "blur"]):
        return "Ophthalmologist"

    # ENT
    elif any(x in text for x in ["ear", "nose", "throat", "cold", "sinus", "cough"]):
        return "ENT Specialist"

    # STOMACH
    elif any(x in text for x in ["stomach", "abdomen", "digestion", "gas"]):
        return "Gastroenterologist"

    # BRAIN
    elif any(x in text for x in ["headache", "migraine", "brain", "nerve"]):
        return "Neurologist"

    # DEFAULT
    return "General Physician"


# =========================
# 🏆 GET BEST DOCTOR FROM DB (FIXED)
# =========================
def get_best_doctor(specialization):
    from database import connect_db

    conn = connect_db()
    cursor = conn.cursor()

    print("Searching for specialization:", specialization)

    # 🔥 TRY EXACT MATCH
    cursor.execute("""
        SELECT name, specialization, rating 
        FROM doctors 
        WHERE specialization=%s
        ORDER BY rating DESC
        LIMIT 1
    """, (specialization,))

    result = cursor.fetchone()
    print("Result from DB:", result)

    # 🔥 FIXED FALLBACK (NO RANDOM DOCTOR)
    if not result:

        print("⚠️ No exact match found, using safe fallback")

        # 👉 fallback to General Physician ONLY
        cursor.execute("""
            SELECT name, specialization, rating 
            FROM doctors 
            WHERE specialization='General Physician'
            ORDER BY rating DESC 
            LIMIT 1
        """)

        result = cursor.fetchone()

    conn.close()

    if result:
        return result[0], result[2], result[1]

    return "No Doctor Found", 0, "Unknown"
# =========================
# 🤖 MAIN CHATBOT FUNCTION
# =========================
def chatbot_response(user_input, role):

    appointment_needed = False
    emergency = False

    # 🚨 EMERGENCY CHECK
    if check_emergency(user_input):
        return (
            "High blood pressure detected. Seek immediate medical attention.",
            True,
            True,
            "Emergency Doctor"
        )

    # 🔥 APPOINTMENT TRIGGER
    keywords = ["severe", "pain", "fever", "injury", "high"]
    if any(word in user_input.lower() for word in keywords):
        appointment_needed = True

    # 🔥 SIMPLE AI PROMPT
    prompt = f"""
You are a healthcare assistant.

Rules:
- Do NOT assume disease
- Use simple English
- Give 3 short sentences

1. Possible reason
2. Simple advice
3. Suggest doctor type

Problem: {user_input}
"""

    try:
        response = requests.post(
            "http://localhost:1234/v1/chat/completions",
            json={
                "model": "phi-3.1-mini-4k-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 100
            }
        )

        if response.status_code != 200:
            return ("Error connecting to AI", False, False, "General Doctor")

        data = response.json()
        text = data["choices"][0]["message"]["content"].strip()

    except:
        return ("AI not responding", False, False, "General Doctor")

    # =========================
    # 🧹 CLEAN TEXT
    # =========================
    text = text.replace("\n", " ").strip()
    text = re.sub(r'\b\d+\.\s*', '', text)

    # REMOVE BAD WORDS
    bad_words = ["software", "engineer", "system", "code", "bug"]
    for word in bad_words:
        if word in text.lower():
            text = ""

    # FALLBACK
    if len(text) < 20:
        text = "Body pain may be due to strain. Take rest and see doctor."

    # SPLIT SENTENCES
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    clean_sentences = []
    for s in sentences:
        if len(s.split()) <= 10:
            clean_sentences.append(s)
        if len(clean_sentences) == 3:
            break

    if len(clean_sentences) < 3:
        clean_sentences = sentences[:3]

    final_output = ". ".join(clean_sentences)

    # LIMIT WORDS
    words = final_output.split()
    final_output = " ".join(words[:25])

    # ENSURE DOCTOR LINE
    if "doctor" not in final_output.lower():
        final_output += " See a doctor."

    if not final_output.endswith("."):
        final_output += "."

    # =========================
    # 👨‍⚕️ GET BEST DOCTOR
    # =========================
    specialization = suggest_doctor(user_input)
    doctor, rating, specialization = get_best_doctor(specialization)

    return final_output, appointment_needed, emergency, doctor, rating ,specialization