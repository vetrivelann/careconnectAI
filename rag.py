from chatbot import suggest_doctor, get_best_doctor
import requests

def analyze_report(report_text):

    prompt = f"""
You are a healthcare assistant.

Based on this medical report:

{report_text}

Give:
1. Short summary
2. Simple advice
3. Suggest doctor type

Use simple English
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
                "max_tokens": 120
            }
        )

        data = response.json()
        text = data["choices"][0]["message"]["content"].strip()

    except:
        return "Error analyzing report", "General Doctor", 0

    specialization = suggest_doctor(text)
    doctor, rating, specialization = get_best_doctor(specialization)

    return text, doctor, rating, specialization