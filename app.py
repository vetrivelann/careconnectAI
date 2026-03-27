import streamlit as st
from chatbot import chatbot_response
from ocr import extract_text, extract_patient_name
import datetime
from database import connect_db
import uuid
import re
from rag import analyze_report
import pandas as pd
import matplotlib.pyplot as plt

st.title("🏥 CareConnect AI")

# =========================
# SESSION STATE
# =========================
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "response" not in st.session_state:
    st.session_state.response = ""

if "emergency" not in st.session_state:
    st.session_state.emergency = False

if "emergency_flag" not in st.session_state:
    st.session_state.emergency_flag = False

if "emergency_patient" not in st.session_state:
    st.session_state.emergency_patient = ""

if "doctor" not in st.session_state:
    st.session_state.doctor = ""

if "rating" not in st.session_state:
    st.session_state.rating = 0

if "specialization" not in st.session_state:
    st.session_state.specialization = ""

# =========================
# ROLE
# =========================
role = st.selectbox("Select Role", ["Patient", "Nurse", "Doctor", "Admin"])
st.info(f"👤 You are logged in as: {role}")

# =====================================================
# 🤖 PATIENT
# =====================================================
if role == "Patient":

    user_input = st.text_input("Enter your message")

    if st.button("Send"):
        if user_input:
            response, appointment_needed, emergency, doctor, rating, specialization = chatbot_response(user_input, role)

            sentences = re.split(r'[.!?]', response)
            sentences = [s.strip() for s in sentences if s.strip()]
            response = ". ".join(sentences[:3])

            st.session_state.response = response
            st.session_state.emergency = emergency
            st.session_state.show_form = emergency

            st.session_state.doctor = doctor
            st.session_state.rating = rating
            st.session_state.specialization = specialization

    if st.button("🔄 Refresh"):
        st.session_state.response = ""
        st.session_state.show_form = False
        st.session_state.emergency = False
        st.rerun()

    if st.session_state.response:
        st.success("🧠 AI Response")
        st.write(st.session_state.response)

        if st.session_state.doctor:
            st.success(f"👨‍⚕️ Doctor: {st.session_state.doctor}")
            st.write(f"🩺 Specialization: {st.session_state.specialization}")
            st.write(f"⭐ Rating: {st.session_state.rating}")

    if st.session_state.emergency:
        st.error("🚨 Emergency Alert!")

    if not st.session_state.show_form and st.session_state.response:
        if st.button("📅 Book Appointment"):
            st.session_state.show_form = True

    if st.session_state.show_form:
        st.warning("⚠️ Book appointment")

        name = st.text_input("Name")
        date = st.date_input("Date")
        time = st.time_input("Time")

        if st.button("Book Appointment"):
            conn = connect_db()
            cursor = conn.cursor()

            appointment_id = str(uuid.uuid4())

            cursor.execute(
                "INSERT INTO appointments VALUES (%s,%s,%s,%s,%s)",
                (
                    appointment_id,
                    name,
                    str(date),
                    str(time),
                    st.session_state.doctor
                )
            )

            conn.commit()
            st.success(f"Appointment booked with {st.session_state.doctor}!")

    # 🔥 FIX 1: OCR ONLY FOR PATIENT
    st.divider()
    st.subheader("📄 Upload Medical Report")

    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["png", "jpg", "jpeg"],
        key="patient_ocr"
    )

    if uploaded_file:
        text = extract_text(uploaded_file)

        if st.button("Analyze Report"):
            result, doctor, rating, specialization = analyze_report(text)

            st.success("🧠 AI Report Analysis")
            st.write(result)
            st.success(f"👨‍⚕️ Doctor: {doctor}")
            st.write(f"🩺 Specialization: {specialization}")
            st.write(f"⭐ Rating: {rating}")

        st.success("Extracted Text:")
        st.write(text)

# =====================================================
# 🩺 NURSE
# =====================================================
if role == "Nurse":

    # 🔥 FUNCTION (UPDATED)
    def nurse_suggest_doctor(temp, bp, pulse):

        # --- BP CHECK ---
        if "/" in bp:
            sys, dia = map(int, bp.split("/"))
            if sys >= 180 or dia >= 120:
                return "Emergency Specialist"
            elif sys >= 140 or dia >= 90:
                return "Cardiologist"
        else:
            if int(bp) >= 180:
                return "Emergency Specialist"

        # --- PULSE CHECK ---
        if pulse > 120:
            return "Emergency Specialist"
        elif pulse > 100:
            return "Cardiologist"

        # --- TEMPERATURE CHECK (FIXED) ---
        if temp >= 40:
            return "Emergency Specialist"
        elif temp >= 38:
            return "General Physician"

        return "General Physician"

    st.subheader("🩺 Enter Patient Vitals")

    # 🔄 REFRESH BUTTON
    if st.button("🔄 Refresh"):
        for key in ["temp", "bp", "pulse", "emergency_flag", "emergency_patient"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    patient_name = st.text_input("Patient Name")
    temp = st.number_input("Temperature (°C)")
    bp = st.text_input("Blood Pressure (e.g., 120/80)")
    pulse = st.number_input("Pulse")

    # 🔥 SAVE VITALS
    if st.button("Save Vitals"):

        if not patient_name:
            st.error("Enter patient name")
        else:
            conn = connect_db()
            cursor = conn.cursor()

            vital_id = str(uuid.uuid4())

            cursor.execute("""
            INSERT INTO vitals VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                vital_id,
                patient_name,
                temp,
                bp,
                pulse,
                str(datetime.datetime.now())
            ))

            conn.commit()
            st.success("Vitals saved!")

            # 🔥 STORE VALUES
            st.session_state.temp = temp
            st.session_state.bp = bp
            st.session_state.pulse = pulse
            st.session_state.emergency_patient = patient_name

            # 🔥 CHECK EMERGENCY
            emergency_flag = False

            # --- BP CHECK ---
            try:
                if "/" in bp:
                    sys, dia = map(int, bp.split("/"))
                else:
                    sys = int(bp)
                    dia = 80
            except:
                st.error("Invalid BP format! Use 120/80")
                st.stop()

            if sys >= 180 or dia >= 120:
                st.error("🚨 CRITICAL BP! Immediate attention needed")
                emergency_flag = True
            elif sys >= 140 or dia >= 90:
                st.warning("⚠️ High Blood Pressure")
            elif sys < 90 or dia < 60:
                st.warning("⚠️ Low Blood Pressure")

            # --- TEMP CHECK ---
            if temp >= 40:
                st.error("🚨 Very High Fever (Critical)")
                emergency_flag = True
            elif temp >= 38:
                st.warning("⚠️ Fever detected")

            # --- PULSE CHECK ---
            if pulse > 120:
                st.error("🚨 Dangerous Pulse Rate")
                emergency_flag = True
            elif pulse > 100:
                st.warning("⚠️ High Pulse")

            # 🔥 FINAL STATUS
            if emergency_flag:
                st.warning("⚠️ Emergency detected!")
                st.session_state.emergency_flag = True
            else:
                st.success("✅ Patient is stable")

                # 🤖 AI HEALTH MESSAGE
                import random
                tips = [
                    "💧 Drink plenty of water",
                    "🏃 Do daily exercise",
                    "🥗 Eat healthy foods",
                    "😴 Maintain proper sleep",
                    "🧘 Reduce stress"
                ]
                st.info("🤖 AI Suggestion: " + random.choice(tips))

    # 🔥 EMERGENCY BOOKING
    if st.session_state.get("emergency_flag", False):

        st.error("🚨 Emergency! Book now")

        date = st.date_input("Date")
        time = st.time_input("Time")

        if st.button("Book Emergency"):

            conn = connect_db()
            cursor = conn.cursor()

            appointment_id = str(uuid.uuid4())

            # 🔥 USE STORED VALUES
            temp = st.session_state.temp
            bp = st.session_state.bp
            pulse = st.session_state.pulse

            # 🔥 GET DOCTOR
            specialization = nurse_suggest_doctor(temp, bp, pulse)

            from chatbot import get_best_doctor
            doctor, rating, specialization = get_best_doctor(specialization)

            cursor.execute(
                "INSERT INTO appointments VALUES (%s,%s,%s,%s,%s)",
                (
                    appointment_id,
                    st.session_state.emergency_patient,
                    str(date),
                    str(time),
                    doctor
                )
            )

            conn.commit()

            st.success(f"🚨 Emergency booked with {doctor} ({specialization}) ⭐ {rating}")

            st.session_state.emergency_flag = False

# =====================================================
# 👨‍⚕️ DOCTOR
# =====================================================
if role == "Doctor":

    st.subheader("👨‍⚕️ Doctor Dashboard")

    conn = connect_db()
    cursor = conn.cursor()

    # 🔹 VIEW APPOINTMENTS
    st.write("### 📅 Appointments")

    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()

    patient_list = []

    for row in appointments:
        st.write(f"{row[1]} | {row[2]} | {row[3]} | {row[4]}")
        patient_list.append(row[1])

    st.divider()

    # 🔹 SELECT PATIENT
    if patient_list:
        selected_patient = st.selectbox("Select Patient", list(set(patient_list)))
    else:
        st.warning("No patients found")
        selected_patient = None

    st.divider()

    # 🔹 VIEW PATIENT HISTORY
    if selected_patient:
        st.write("### 🧾 Patient History")

        cursor.execute("SELECT * FROM vitals WHERE patient_name=%s", (selected_patient,))
        vitals = cursor.fetchall()

        if vitals:
            for v in vitals:
                st.write(f"Temp: {v[2]} | BP: {v[3]} | Pulse: {v[4]}")
        else:
            st.info("No history found")

    st.divider()

    # 🔹 PRESCRIPTION FORM
    st.write("### 💊 Give Prescription")

    disease = st.text_input("Disease Name")
    medicine = st.text_input("Medicine Name")
    dosage = st.text_input("Dosage (e.g., twice daily)")
    notes = st.text_area("Notes")
    follow_up = st.date_input("Follow-up Date")

    if st.button("Save Prescription"):

        if not selected_patient or not disease or not medicine:
            st.error("Fill all required fields")
        else:
            prescription_id = str(uuid.uuid4())

            cursor.execute("""
            INSERT INTO prescriptions 
            (prescription_id, patient_name, doctor_name, medicine, dosage, notes, date, follow_up)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                prescription_id,
                selected_patient,
                "Doctor",   # you can change dynamically later
                medicine,
                dosage,
                notes,
                str(datetime.date.today()),
                str(follow_up)
            ))

            conn.commit()
            st.success("💊 Prescription saved successfully!")

    st.divider()

    # 🔹 DISCHARGE SUMMARY
    st.write("### 🏥 Discharge Summary")

    summary = st.text_area("Enter discharge summary")

    if st.button("Save Discharge"):

        if not selected_patient or not summary:
            st.error("Enter summary")
        else:
            discharge_id = str(uuid.uuid4())

            cursor.execute("""
            INSERT INTO discharge 
            (discharge_id, patient_name, doctor_name, summary, date)
            VALUES (%s,%s,%s,%s,%s)
            """, (
                discharge_id,
                selected_patient,
                "Doctor",
                summary,
                str(datetime.date.today())
            ))

            conn.commit()
            st.success("🏥 Discharge summary saved!")

    conn.close()
# =====================================================
# 📊 ADMIN DASHBOARD 
# =====================================================
if role == "Admin":

    st.title("📊 Admin Dashboard")

    # 🔄 Refresh Button
    if st.button("🔄 Refresh"):
        st.rerun()

    conn = connect_db()
    cursor = conn.cursor()

    # =============================
    # 📊 COUNTS
    # =============================
    cursor.execute("SELECT COUNT(*) FROM vitals")
    vitals_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM doctors")
    doctors_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments")
    appointments_count = cursor.fetchone()[0]

    # 📄 REPORTS (using vitals)
    reports_count = vitals_count

    # =============================
    # 📊 DISPLAY METRICS
    # =============================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🩺 Nurse Records", vitals_count)
    col2.metric("🧑‍⚕️ Doctors", doctors_count)
    col3.metric("📅 Appointments", appointments_count)
    col4.metric("📄 Reports", reports_count)

    st.divider()

    # =============================
    # 📊 DOCTORS BY SPECIALIZATION
    # =============================
    st.subheader("🧑‍⚕️ Doctors by Specialization")

    cursor.execute("""
        SELECT specialization, COUNT(*) 
        FROM doctors 
        GROUP BY specialization
    """)
    data = cursor.fetchall()

    if data:
        import pandas as pd
        df = pd.DataFrame(data, columns=["specialization", "count"])
        st.bar_chart(df.set_index("specialization"))
    else:
        st.info("No doctor data available")

    # =============================
    # 📋 RECENT APPOINTMENTS
    # =============================
    st.subheader("📅 Recent Appointments")

    cursor.execute("""
        SELECT * FROM appointments
        ORDER BY date DESC, time DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()

    if rows:
        import pandas as pd
        df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No appointments available")

    # =============================
    # 📄 REPORT INFO
    # =============================
    st.success(f"📄 Total Reports Generated: {reports_count}")

    conn.close()