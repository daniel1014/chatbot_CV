import streamlit as st
# from RAG_utils import (initialize_qdrant_client, 
#                        qdrant_scroll, 
#                        qdrant_add, qdrant_delete, load_text_from_docx, chunk_text)
import RAG_utils
import pandas as pd

# status_placeholder = st.empty()
# if "success" in st.session_state:
#     status_placeholder.success(st.session_state["success"])
#     del st.session_state["success"]

st.subheader("AECOM IPC CV Database Admin Panel")
st.logo("assets/logo_reverse.png")

tab1, tab2 = st.tabs(["View Documents from Database", "Upload Document"])

# def delete_document():
#     selected_row = st.session_state['selected_row']
#     if selected_row:
#         selected_filename = df.iloc[selected_row[0]]["filename"]
#         RAG_utils.qdrant_delete(qdrant_client, st.session_state.collection_name, selected_filename)
#         # st.rerun()
#         st.success(f"Successfully deleted {selected_filename}")
#     else:
#         st.info("Please select a document to delete")

with tab1:
    @st.experimental_dialog("Delete Confirmation")
    def delete_confirm():
        selected_filename = df.iloc[selected_row[0]]["filename"]
        st.write(f"Are you sure you want to delete the selected document - ***{selected_filename}***?")
        if st.button("Submit", type="primary"):
            RAG_utils.qdrant_delete(qdrant_client, st.session_state.collection_name, selected_filename)     # delete the selected document
            st.session_state['delete_success'] = f"Successfully deleted ***{selected_filename}***"  # display success message
            st.rerun()      # refresh the page
      

    # Fetch documents from Qdrant collection
    qdrant_client = RAG_utils.initialize_qdrant_client()
    
    # Fetch all documents from the collection
    st.session_state['stored_docs'] = RAG_utils.qdrant_scroll(qdrant_client, st.session_state.collection_name)
    if st.session_state.stored_docs['filename']:
        df = pd.DataFrame(st.session_state['stored_docs'], index=range(1, len(st.session_state['stored_docs']['filename'])+1))
            
        # Display documents in a dataframe
        data = st.dataframe(data=df, on_select="rerun", selection_mode="single-row", use_container_width=True, key="data",
                            column_config={"filename": "File name", 
                                           "team": "Team", 
                                           "_index": st.column_config.Column(
                                               "Item",
                                               width=10)
                                             })
        status_placeholder = st.empty()
        if "delete_success" in st.session_state:
            status_placeholder.success(st.session_state["delete_success"], icon=":material/delete_forever:")
            del st.session_state["delete_success"]
        if st.button("Delete Selected Document"):
            selected_row = st.session_state.data['selection']['rows']
            if selected_row:
                # selected_filename = df.iloc[selected_row[0]]["filename"]
                # RAG_utils.qdrant_delete(qdrant_client, st.session_state.collection_name, selected_filename)
                # st.session_state['stored_docs'] = RAG_utils.qdrant_scroll(qdrant_client, st.session_state.collection_name)
                # st.success(f"Successfully deleted {selected_filename}")
                delete_confirm()
            else:
                st.info("Please select a document to delete", icon=":material/error:")
    else:
        st.warning("No documents found in the vector database", icon="⚠️")
    st.button("Refresh", type="secondary")


with tab2:
    st.info("Please upload one or multiple CV files and select the corresponding Team for the uploading CV...")
    # with st.expander("See explanation"):
    #     st.write(''':orange[You can upload your CV to the database here.  
    #             By doing so, the CV will be processed and securely stored in the cloud database,    
    #             enhancing the AI chatbot's response capabilities.]''')
    uploaded_files = st.file_uploader("Choose a file", type=["docx"], accept_multiple_files=True, 
                                      help= ''':orange[You can upload your CV to the database here.  
                By doing so, the CV will be processed and securely stored in the cloud database,    
                enhancing the AI chatbot's response capabilities.]''')
    team = st.selectbox(
    "What is your team in IPC?",
    ("Data Advisory", "Planning", "Controls", "Risk"),
    index=None,
    placeholder="Select the team for the uploading CV...",
    )
    
    if uploaded_files is not None and team:
        if st.button("Process and Upload"):
            # Process the document
            for uploaded_file in uploaded_files:
                text = RAG_utils.load_text_from_docx(uploaded_file)
                chunks = RAG_utils.chunk_text(text)
        
                # Create metadata
                metadata = [{"filename": uploaded_file.name,"team": team} for _ in range(len(chunks))]
                
                # Initialize Qdrant collection
                RAG_utils.qdrant_add(
                    qdrant_client,
                    collection_name=st.session_state.collection_name,
                    chunks=chunks,
                    metadata=metadata,
                )
                print(f"Added {uploaded_file.name} with {len(chunks)} chunks to the collection")
            st.success(f"Successfully processed and uploaded ***{[file.name for file in uploaded_files]}*** to the database")

st.sidebar.write(f"*You are logged in as {st.session_state.role}*" if st.session_state.role else "*You are not logged in*")
# st.session_state

