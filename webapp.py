import os
import streamlit as st
from globals import file_manager, knowledge_manager, chat_manager
from streamlit_chat import message
from utils import sanitize_filename
import uuid



def main():
    page = st.sidebar.selectbox("Page", ["Upload Files", "Chat"])
    
    if page == "Upload Files":
        file_upload()
    elif page == "Chat":
        chat()
        
        
        
def file_upload():
    st.title("DocsGPT")
    
    private_mode = st.sidebar.checkbox("Private Mode", value=False)
    mode = "private" if private_mode else "normal"
    knowledge_manager.switch_mode(mode)
        
    uploaded_file = st.file_uploader("Upload a file")
    
    if uploaded_file is not None:
        name = sanitize_filename(uploaded_file.name)
        
        os.makedirs("files", exist_ok = True)
        unique_id = str(uuid.uuid4())[:8]
        file_name, extension = os.path.splitext(name)
        file_name = f"{file_name}_{unique_id}{extension}"
        
        file_path = os.path.join("files", file_name)
        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())
        
        if not knowledge_manager.add_file(file_path):
            st.write("File not supported!")
        else:
            st.write("File Uploaded Successfully!")
            st.write(f"Filename: {uploaded_file.name}")
            st.write(f"File size: {uploaded_file.size} bytes")
    
    
 
def chat():
    st.title("DocsGPT: Chat with Documents")

    private_mode = st.sidebar.checkbox("Private Mode", value=False)
    mode = "private" if private_mode else "normal"
    knowledge_manager.switch_mode(mode)

    files = file_manager.select_files_with_mode(mode)
    file_list = [file.file_name.replace("files_", "") for file in files]
    selected_file = st.sidebar.selectbox("Select a file", file_list)

    if selected_file: 
        converations = chat_manager.get_all_conversations_for_file(selected_file)

        conversation_title = st.sidebar.selectbox(
            "Select a conversation",
            list({convo.title for convo in converations}),
        )
    else:
        st.write("Please select a file")
        return
    
    conversation_name = st.sidebar.text_input("Enter conversation name:")
    if st.sidebar.button("New Conversation"):
        if conversation_name:
            chat_manager.add_message(str(uuid.uuid4()), "How can i help?", "HI", file_name=selected_file, title=conversation_name)
            st.sidebar.write("Created successfully")
            st.experimental_rerun()
        else:
            st.sidebar.write("Name cannot be empty")
        
    for convo in converations:
        if conversation_title == convo.title:
            conversation_id = convo.namespace
            break
    if converations:
        if prompt := st.text_input("Type your prompt and press Enter"):
            try:
                result = knowledge_manager.chat(f"files_{selected_file}", prompt, chat_manager.retrieve_all_messages(conversation_id))
                if conversation_title == "New":
                    conversation_title = knowledge_manager.get_title([(prompt, result)])

                chat_manager.add_message(conversation_id, result, prompt, file_name=selected_file, title=conversation_title)
            except Exception as e:
                chat_manager.add_message(conversation_id, "Something went wrong", prompt, file_name=selected_file, title=conversation_title)            
    else:
        st.write("Please choose a conversation")

    if converations:
        for i, chat in enumerate(reversed(chat_manager.retrieve_all_messages(conversation_id)), start=1):
            message(chat[1], key=i*1000000)
            message(chat[0], is_user=True, key=i)



    
if __name__ == "__main__":
    main()
