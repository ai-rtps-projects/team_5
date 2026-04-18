import streamlit as st
import os
import google.generativeai as genai

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="University Support Chatbot",
    page_icon="🎓"
)

st.title("🎓 University Support Chatbot")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("⚡ Quick Actions")

selected_option = st.sidebar.selectbox(
    "Choose a quick question:",
    ["-- Select --", "Exam Schedule", "Syllabus", "Contact Details"]
)

quick_query = None
if selected_option == "Exam Schedule":
    quick_query = "exam schedule"
elif selected_option == "Syllabus":
    quick_query = "syllabus"
elif selected_option == "Contact Details":
    quick_query = "contact number"

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.chat = None
    st.rerun()

# ---------------------------
# LOAD KB
# ---------------------------
file_path = os.path.join(os.path.dirname(__file__), "university_chatbot_database_complete.json")

if not os.path.exists(file_path):
    st.error("❌ JSON file not found")
    st.stop()

with open(file_path, "r", encoding="utf-8") as f:
    kb = f.read()

# ---------------------------
# PROMPT
# ---------------------------
prompt = f"""
You are a professional University Student Support Executive. 
Your ONLY source of truth is the JSON database provided below.

DATABASE:
{kb}

STRICT RULES:
1. When a student asks about a specific subject (like "Data Science"), you MUST look for that subject in the 'intents' or 'subject_syllabus_qa' sections.
2. If there is a specific date mentioned for that subject, you MUST provide that exact date.
3. Do NOT give general website links if a specific date is available in the JSON.
4. If asked for a phone number, provide the one listed in the 'escalation_triggers' or 'contacts' section.
"""

# ---------------------------
# INIT GEMINI
# ---------------------------
genai.configure(api_key="")  # <-- ADD YOUR API KEY

if "chat" not in st.session_state or st.session_state.chat is None:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=prompt
    )
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# DISPLAY CHAT (CHATGPT STYLE)
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# INPUT
# ---------------------------
user_input = st.chat_input("Ask your question...")

query = quick_query if quick_query else user_input

# ---------------------------
# HANDLE CHAT
# ---------------------------
if query:
    # Show user message
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append({"role": "user", "content": query})

    # Bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            response = st.session_state.chat.send_message(query)
            reply = response.text if hasattr(response, "text") else str(response)

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
