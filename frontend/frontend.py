import streamlit as st
import requests

API_URL="http://localhost:2024"
st.set_page_config(page_title="AI PDF Agent",page_icon="🤖",layout="centered")
st.title("AI Document Agent")
st.caption("Powered by fastapi langgraph and supabase")

if "messages" not in st.session_state:
    st.session_state.messages=[]
    
with st.sidebar:
    st.header("Upload Document")
    uploader=st.file_uploader("Drop your pdf here",type="pdf")
    if st.button("process pdf",use_container_width=True):
        if uploader is not None:
            with st.spinner("Chunking and Vectorising"):
              files={"file":(uploader.name,uploader.getvalue(),"application/pdf")}
              
              # FIXED 1: 'files=files' not 'file=files'
              response=requests.post(f"{API_URL}/api/ingest",files=files)
              
              if response.status_code ==200:
                  st.success(response.json().get("message","Success !"))
              else:
                  st.error(f"error : {response.text}")
        else:
            st.warning("pehle pdf toh upload kar")

# FIXED 2: Added '.messages'
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your document or math problem"):
    
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # FIXED 3: Changed 'assintant' to 'assistant'
    with st.chat_message("assistant"):
         with st.spinner("Agent is Thinking"):
             try:
                 response=requests.post(f"{API_URL}/api/chat",json={"question":prompt})
                 if response.status_code ==200:
                     answer=response.json().get("answer","i dont know")
                     st.markdown(answer)
                     
                     # FIXED 3: Changed 'assintant' to 'assistant'
                     st.session_state.messages.append({"role":"assistant","content":answer})
                 else:
                    st.error(f"Backend Error: {response.text}")
             except Exception as e:
                st.error(f"Connection Failed! Is FastAPI running on port 2024? Error: {str(e)}")