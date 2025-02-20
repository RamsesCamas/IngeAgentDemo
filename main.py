import streamlit as st
import requests
import time
# Set basic Streamlit page config
st.set_page_config(
    page_title="Chat with Maria Agent (Remote API)",
    page_icon=":speech_balloon:",
    layout="centered",
)

# Add a title
st.title("Chatea con MarIA")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar options
st.sidebar.header("Settings")
api_mode = st.sidebar.radio("Escoge modo API:", ["MarIA base", "Agente Ingenieria"])

if api_mode == "MarIA base":
    role = st.sidebar.selectbox("Selecciona tu rol", ["user", "engineer", "admin"], index=0)

st.sidebar.markdown("""
**Instrucciones**  
1. Escoge entre `MarIA base` or `Agente Ingenieria`.  
2. Si use `MarIA base`, seleccione un rol (`user`, `engineer`, or `admin`).  
3. Ingrese su mensaje y de Enter o click en el icono de flecha.  
""")

# Display previous conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if user_input := st.chat_input("Type your message here..."):
    # 1. Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    user_input = user_input + ". Answer in Spanish always, even your thinking."
    # 2. Prepare API call
    if api_mode == "MarIA base":
        api_url = "http://50.28.84.22:8000/chat/"
        payload = {
            "prompt": user_input,
            "user": "exampleUser",
            "role": role
        }
    else:  # RAG Query
        api_url = "http://50.28.84.22:8000/rag-query/"
        payload = {"prompt": user_input}

    # 3. Send request to FastAPI
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            assistant_full_response = data.get("response", "No response received.")
            print(assistant_full_response)
            try:
                assistant_response = assistant_full_response['response']
            except:
                assistant_response = assistant_full_response
            if len(assistant_response) == 0 or assistant_response == '<think>':
                try:
                    assistant_response = assistant_full_response['content']
                except:
                    assistant_response = assistant_full_response['sources'][0]['content']
            
        else:
            assistant_response = f"**Error {response.status_code}**: {response.text}"
    except requests.exceptions.RequestException as e:
        assistant_response = f"Request failed: {str(e)}"

    def stream_response(text):
        for word in text.split():
            yield word + " "
            time.sleep(0.05)  # Pequeño retraso para simular el flujo de respuesta

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    with st.chat_message("assistant"):
        st.write_stream(stream_response(assistant_response))