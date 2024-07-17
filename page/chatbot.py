import streamlit as st
import os
from dotenv import dotenv_values
# from unstructured.partition.auto import partition
import RAG_utils
import uuid

st.header(":orange[Start chatting with the IPC CV chatbot]")

st.logo("assets/logo_reverse.png")
config = dotenv_values(".env")

with st.sidebar:
    tab1, tab2 = st.tabs(["Basic", "Advanced"])
    with tab1:
        st.title('Filters')
        team_filter = st.selectbox("Team (optional)", ["Data Advisory", "Risk", "Controls", "Planning"], index=None, 
                                   placeholder = "Select Team within IPC",
                                   help=":orange[Select a team to filter the documents by team affiliation.]")
        # a text input to filter any keywords in the doucments
        text_filter = st.text_input("Full-text search (optional)", placeholder = "Type keyword, e.g. machine learning ", 
                                    help=''':orange[Enter any keywords to filter the documents by full-text search.  
                                    It will narrow the response of the chatbot and enhance the accuracy.]''')

    with tab2:
        st.subheader('Advanced settings')
        preamble_template= st.text_area('Preamble Template', 
        '''
            
        ## Task and Context
        You are a senior business analyst at AECOM, tasked with analysing a range of internal CVs from team members within the Infrastructure Projects Consulting (IPC) division. Your analysis includes interpreting metadata such as filenames, which contain each colleague's role and full name, and team affiliations, to provide summaries and insights that support strategic decision-making processes.

        ## Style Guide
        Use British spelling, and maintain a professional tone.
        ''',
        help="This is a system message which guides how the model should behave throughout to generate a response. It can be considered as instructions for the model which outline the goals and behaviors for the conversation (recommend to follow the specific structure and format for optimal performance).")
    

# initialize chat 
if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'assistant', 'content': 'Hello! How can I help you today?'}]

# display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# clear chat history button
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]
    st.session_state['conversation_id'] = str(uuid.uuid4())
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# initialize Cohere and Qdrant clients
co = RAG_utils.initialize_cohere_client()
qdrant_client = RAG_utils.initialize_qdrant_client()

if prompt := st.chat_input("Ask a question about the uploaded CVs"):
    if 'conversation_id' not in st.session_state:
        st.session_state['conversation_id'] = str(uuid.uuid4())

    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        text_placeholder = st.empty()
        with status_placeholder.status("Thinking...") as status:
            response_query = co.chat(message=prompt, search_queries_only=True, conversation_id=st.session_state.conversation_id)
            # If there are search queries, retrieve document chunks and respond
            if response_query.search_queries:
                documents = []
                for query in response_query.search_queries:
                    st.write(f"Generated query: *{query.text}*")
                    # Get documents from Qdrant semantic search engine
                    docs_retrieved = RAG_utils.qdrant_search(qdrant_client, collection_name=st.session_state.collection_name, query=query.text, 
                                                             team_filter=team_filter, text_filter=text_filter, top_k=5)
                    documents.extend(docs_retrieved)
                # for doc in documents:
                #     print(doc)

                # Use document chunks to respond
                response = co.chat_stream(
                    message = prompt,
                    model="command-r",
                    documents=documents,
                    conversation_id=st.session_state.conversation_id,
                    preamble = preamble_template
                )
            else:
                st.write(f"No search queries found. Responding directly to the user message...")
                response = co.chat_stream(
                    message = prompt,
                    model="command-r",
                    conversation_id=st.session_state.conversation_id,
                )

            full_response = ''
            for event in response:
                if event.event_type == "text-generation":
                    full_response += event.text
                    text_placeholder.markdown(full_response)
                elif event.event_type == "search-results":
                    print(event.documents)
            # Record the conversation 
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            status.update(label="Complete!", state="complete")

st.sidebar.write(f"*You are logged in as {st.session_state.role}*" if st.session_state.role else "*You are not logged in*")

# st.session_state
