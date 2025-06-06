import streamlit as st
from openai import OpenAI
import pandas as pd
import base64

APP_TITLE = "Automatic analysis of CSV data based on large models"

def display_chat_messages():
    """Displays the chat messages from session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def initialize_chat_history():
    """Initializes chat history in session state if it doesn't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
def get_ai_response(client, user_prompt, system_prompt):
    """
    Gets a response from the AI model.
    """
    try:
        # Construct the message history for the API call
        # This includes the system prompt and the current conversation
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        # Add the current user prompt
        # api_messages.append({"role": "user", "content": user_prompt}) # Already added before calling

        response = client.chat.completions.create(
            model="deepseek-chat",  # Or your specific DeepSeek model
            messages=api_messages, # Send the whole conversation history
            temperature=0.7, # Adjust for creativity vs. factuality
            # max_tokens=500, # Optional: limit response length
        )
        #st.write(response.choices[0])
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error communicating with the AI: {e}")
        return None

st.set_page_config(page_title=f"{APP_TITLE}", layout="wide")
    
st.markdown(f'''
    <h1 style="text-align: center; font-size: 26px; font-weight: bold; color: black; background: #B9CDE6; border-radius: 0.5rem; margin-bottom: 15px;">
        {APP_TITLE}
    </h1>''', unsafe_allow_html=True)
    
api_key = "sk-ad5184cc837d4a6c9860bfa46ddd2c68" # Hardcoded API Key
    
with st.sidebar.expander("**API Configuration**", True):
    base_url = st.text_input("Enter your API Base URL", value="https://api.deepseek.com/v1", key="myapp")
    st.info("Note: Your API key is pre-configured for this session.")
    
uploaded_file = st.sidebar.file_uploader("Please upload a csv file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
        
    file_bytes = uploaded_file.getvalue()
    base64_str = base64.b64encode(file_bytes).decode('utf-8')
        
    with st.expander("**Upload file show**", True):
        st.dataframe(df, use_container_width=True)
else:
    st.info("Note: Please input a file to start!!!")
    try:<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="32" height="32" rx="8" fill="#0D0D0D" fill-opacity="0.5"/>
<path d="M16.7491 13.5244C16.9453 13.3351 17.257 13.338 17.4497 13.5307L18.5937 14.6747C18.7865 14.8675 18.7893 15.1792 18.5999 15.3754L11.5512 22.6792C11.3571 22.8804 11.0356 22.8832 10.8379 22.6855L9.43649 21.2841C9.23872 21.0863 9.24163 20.7648 9.44294 20.5706L16.7491 13.5244Z" stroke="white" stroke-width="1.5"/>
<path d="M14.5 15.4998L16.5 17.4998" stroke="white" stroke-width="1.5"/>
<path d="M16.25 9V10.75" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
<path d="M21.2374 10.7627L20 12.0001" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
<path d="M21.2374 20.7501L20 19.5127" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
<path d="M11.25 10.7627L12.4874 12.0001" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
<path d="M21.25 15.75H23" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
</svg>

        st.session_state.messages = []
    except:
        pass
        
with st.sidebar.expander("**How to use:**", True):
    st.markdown("""
        1. Enter your DeepSeek API Key and Base URL in the sidebar.
        2. Upload a csv file
        3. Input your request text (e.g. Generate analytics visualization dashboard html by uploading data and return only html code.)
        4. You do not need to return data parsed by CSV Base64
        """)
    with open("ai_dev_productivity.csv", "rb") as f:
        csv = f.read()
    st.download_button(
        label="Download example csv file",
        data=csv,
        file_name='ai_dev_productivity.csv',
        mime='text/csv',
        use_container_width=True
    )

client = None
if base_url: # API key is now hardcoded, only check for base_url
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        st.toast("API client configured successfully!", icon="✅")
    except Exception as e:
        st.toast(f"Failed to configure API client: {e}", icon="🚨")
else:
    st.toast("Please enter the API Base URL to proceed.", icon="ℹ️")
  
initialize_chat_history()
display_chat_messages()

if uploaded_file is not None:
    # System prompt to guide the AI
    system_prompt = f"""
    User upload CSV Base64 data:"{base64_str}".
    You are a data analyst by design, analyzing the CSV Base64 data uploaded by the user on a per-user basis.
    1. Make sure your answers analyze the data as multi-dimensionally as possible
    2. Ensure accuracy and authenticity of the answer data
    3. Answers need to be professional
    """
    
    tt = f"CSV Base64 data: '''{base64_str}''', "

    # Get user input
    user_prompt = st.chat_input("What can I help you with today?")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.spinner("Thinking..."):
            ai_response = get_ai_response(client, user_prompt, system_prompt)

        if ai_response:
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)
