import streamlit as st
from transformers import pipeline
import json
import requests

# Load emotion model
@st.cache_resource
def load_model():
    return pipeline("text-classification", model="nateraw/bert-base-uncased-emotion")

model = load_model()

# Emotion mapping
emotion_map = {
    "anger": "Angry",
    "sadness": "Sad",
    "joy": "Happy",
    "fear": "Fear",
    "love": "Love",
    "surprise": "Surprised"
}

# Subcategory mapping for sadness
def get_sadness_subcategory(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["overwhelmed", "burnout", "stressed", "pressure"]):
        return "Stressed"
    elif any(word in text_lower for word in ["empty", "worthless", "hopeless", "depressed", "numb"]):
        return "Depression"
    elif any(word in text_lower for word in ["alone", "isolated", "lonely", "abandoned"]):
        return "Loneliness"
    else:
        return "Sad"

# Streamlit UI
st.title("🧠 let me analysis your Emotion")
name = st.text_input("Enter your name")
text = st.text_area("Describe your feeling")

if st.button("Detect Emotion and Send"):
    if not name.strip() or not text.strip():
        st.warning("Please provide both name and text.")
    else:
        # Run model
        result = model(text)[0]
        label = result["label"].lower()

        if label == "sadness":
            readable_emotion = get_sadness_subcategory(text)
        else:
            readable_emotion = emotion_map.get(label, label.capitalize())

        # Prepare JSON
        data = {
            "UserName": name,
            "Emotion": readable_emotion
        }

        st.subheader("📦 Emotion JSON:")
        st.code(json.dumps(data, indent=2), language="json")

        # Google Apps Script Web App URL
        webhook_url = "https://script.google.com/macros/s/AKfycbx-35LOrAXI_CJMu1aZy63Kqcf9fL7r0Ts-QkO4KZSW4HH187UTSJjR6UrTDsLMhJyA/exec"

        # Send data to Google Sheet
        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 200:
                st.success("✅ Data sent to Google Sheet successfully!")
            else:
                st.error(f"⚠️ Failed with status code: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error sending data: {e}")
