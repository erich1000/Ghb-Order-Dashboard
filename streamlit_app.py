import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Dashboard Setup
st.set_page_config(page_title="Order Dashboard", layout="wide")

# API Verbindung sicherstellen
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🔑 API Key fehlt in den Secrets!")

def parse_sms_with_gemini(sms_text):
    # Wir erzwingen hier die Nutzung des Flash-Modells
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    prompt = f"""
    Extrahiere Daten aus dieser SMS: '{sms_text}'
    Antworte NUR mit validem JSON.
    Format: {{"typ": "Order", "datum": "YYYY-MM-DD", "schicht": "1", "ort": "Ort", "zeit": "6:00-14:00", "rolle": "Beruf"}}
    """
    
    # Der entscheidende Fix: Wir fangen Fehler direkt ab
    try:
        response = model.generate_content(prompt)
        # Säuberung des Textes (falls Markdown ```json drumherum ist)
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_text)
    except Exception as e:
        # Falls das Modell nicht gefunden wird, probieren wir einen alternativen Namen
        if "404" in str(e):
             model_alt = genai.GenerativeModel(model_name="gemini-pro")
             response = model_alt.generate_content(prompt)
             clean_text = response.text.strip().replace("```json", "").replace("```", "")
             return json.loads(clean_text)
        else:
            raise e

st.title("⚓ Mein Schicht-Dashboard")

# Daten-Speicher für die aktuelle Sitzung
if 'orders' not in st.session_state:
    st.session_state.orders = []

with st.expander("Manuelle SMS Eingabe", expanded=True):
    test_sms = st.text_area("SMS Text hier einfügen:")
    if st.button("Analysieren"):
        with st.spinner('Gemini denkt nach...'):
            try:
                data = parse_sms_with_gemini(test_sms)
                st.session_state.orders.append(data)
                st.success("Erfolgreich hinzugefügt!")
            except Exception as e:
                st.error(f"Oje, ein Fehler: {e}")

# Tabelle anzeigen
if st.session_state.orders:
    st.subheader("Deine Schichten")
    df = pd.DataFrame(st.session_state.orders)
    st.table(df) # Wir nutzen .table für eine stabilere Ansicht
