import streamlit as st
from assistant.openai_assistant import *

load_dotenv()

# Retrieve environment variables for thread and assistant configuration
THREAD_ID = os.getenv("THREAD_ID")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

st.title("Personal Travel Assistant")
st.write("Plan your Trip!")

# Initialize the chat history in the session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Your message:"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate a message in the assistant's context and initiate a conversation thread
    create_message(prompt, THREAD_ID)
    run_id = run_thread(THREAD_ID, ASSISTANT_ID)

    with st.spinner("Wait for your Trip..."):
        process_tool_calls(THREAD_ID, run_id)

    messages = retrieve_message_list(THREAD_ID)
    response = messages[0].content[0].text.value

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})