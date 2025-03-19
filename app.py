# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1If1az929dZ0qEBqX4MIgBTZZpHq96pU6
"""

# 📦 Install required packages before running locally:
# pip install streamlit openai

import streamlit as st
import os
from openai import OpenAI

# 🔐 Set your OpenAI API Key
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.warning("Please set your OpenAI API Key in Streamlit Secrets or environment variables.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 📚 Tone options
response_tones = {
    "Formal": "Use a formal and highly professional tone suitable for legal communication.",
    "Neutral": "Use a neutral and professional tone without sounding too rigid.",
    "Friendly Professional": "Use a warm and approachable tone while maintaining professionalism.",
    "Reassuring": "Use a compassionate, supportive tone to reassure the client.",
    "Assertive/Strict": "Use a direct and firm tone to emphasize seriousness without impoliteness.",
    "Instructional/Advisory": "Use a clear and informative tone to explain next steps.",
    "Conciliatory": "Use a diplomatic and tactful tone to de-escalate conflict.",
    "Urgent": "Use a direct and time-sensitive tone to emphasize immediacy.",
    "Empathetic but Objective": "Balance empathy with professionalism."
}

# 🔍 Suggest top 3 tones based on email content
def suggest_tones_from_email(email_text):
    prompt = f"""
You are a legal assistant analyzing a client's email. Suggest the 3 most appropriate response tones from the following list:

- Formal
- Neutral
- Friendly Professional
- Reassuring
- Assertive/Strict
- Instructional/Advisory
- Conciliatory
- Urgent
- Empathetic but Objective

Client Email:
\"\"\"
{email_text}
\"\"\"

Respond with the top 3 tones in a bullet-point list (no numbering) along with a very short clear brief reason for each choice.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# ✍️ Prompt Builder
def build_prompt(email_body, tone_instruction, context_snippet="", signature=""):
    prompt = f"""
You are a legal assistant responding to a client's email at a law firm.

Relevant Case Notes:
{context_snippet}

Client Email:
\"\"\"
{email_body}
\"\"\"

Instructions:
{tone_instruction}

Write a clear, legally appropriate response based on the email above.
If a signature is provided, end the email with this signature:
\"\"\"
{signature}
\"\"\"
"""
    return prompt

# 🤖 Get LLM Draft
def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()

# ============================
# 🌐 Streamlit App Starts Here
# ============================

# 🔄 Session State Defaults
if "email_text" not in st.session_state:
    st.session_state.email_text = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False

st.title("📬 Legal Email Draft Assistant")
st.markdown("Generate professional email responses using AI, tailored for legal firms.")

# 📥 Email Input
email_text = st.text_area("📥 Paste Client Email", value=st.session_state.email_text, height=500)

if st.button("Submit"):
with st.spinner("🔍 Analyzing email content for tone suggestions..."):
    st.session_state.email_text = email_text
    st.session_state.suggestions = suggest_tones_from_email(email_text)
    st.session_state.submitted = True

# 📊 Show Analysis and Tone Selector After Submit
if st.session_state.submitted:
    st.markdown("### 💡 Suggested Response Tones")
    st.markdown(st.session_state.suggestions)

    st.markdown("### ✨ Select Response Tone")
    tone_choice = st.selectbox("Choose a tone for the reply", list(response_tones.keys()))

    context_snippet = st.text_area("📎 Add Case Notes (optional)", placeholder="e.g., lease renewal case, deadline 30th April")

    signature = st.text_area("✍️ Add Your Signature (optional)", placeholder="e.g., Kind regards,\nJohn Smith\nSenior Solicitor")

    if st.button("🧠 Generate Draft Reply"):
        with st.spinner("🤖 Generating response..."):
            tone_instruction = response_tones[tone_choice]
            prompt = build_prompt(st.session_state.email_text, tone_instruction, context_snippet, signature)
            response = get_llm_response(prompt)
        st.markdown("### 📄 Drafted Email Response")
        st.text_area("Generated Email", response, height=500)

