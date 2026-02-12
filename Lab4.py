import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import sys
from pathlib import Path
from PyPDF2 import PdfReader

# working with chromadb on streamlit community cloud
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from chromadb.config import Settings
import chromadb

# create clients 
if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)
if 'claude_client' not in st.session_state:
    claude_api_key = st.secrets["CLAUDE_API_KEY"]
    st.session_state.claude_client = Anthropic(api_key=claude_api_key)


# extract text from pdf
def extract_text_from_pdf_path(pdf_path):

    '''
    this function extracts text from each syllabus 
    to pass to add_to_collection
    '''

    text = ""
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# create chromadb client
chroma_client = chromadb.PersistentClient(path="./ChromaDB_for_Lab")
collection = chroma_client.get_or_create_collection("Lab4Collection")

## using chromadb with openai embeddings ##

def add_to_collection(collection, text, file_name):

    '''
    function to add documents to collections
    
    collection: chromadb collection, already established
    text: extracted text from pdf files
    
    embeddings interested into the collection from openai
    '''

    # create an embedding
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )

    # get embedding
    embedding = response.data[0].embedding

    # add embedding and document to chromadb
    collection.add(
        documents=[text],
        ids=[file_name],
        embeddings=[embedding]
    )

# populate collection with pdfs
def load_pdfs_to_collection(folder_path, collection):

    '''
    this function uses extract_text_from_pdf and 
    add_to_collection to put syllabi in chromadb collection
    '''

    loaded_files = []

    folder = Path(folder_path)

    # Loop through all PDF files in the folder
    for pdf_file in folder.glob("*.pdf"):

        # Extract text from the PDF
        text = extract_text_from_pdf_path(pdf_file)

        # Add to ChromaDB
        add_to_collection(collection, text, pdf_file.name)

        loaded_files.append(pdf_file.name)

    return loaded_files

# check if collection is empty and load PDFs
if collection.count() == 0:
    loaded = load_pdfs_to_collection('./Lab-04-Data/', collection)

def get_rag_context(query):

    '''
    query chromadb for relevant information based on user query
    '''

    # create embedding for query
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=query,
        model='text-embedding-3-small'
    )

    # get embedding
    query_embedding = response.data[0].embedding

    # get text related to this question (this prompt)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    # combine the retrieved documents into context
    if results['documents'][0]:
        context = "\n\n---\n\n".join(results['documents'][0])
        source_files = results['ids'][0]
        return context, source_files
    else:
        return None, None
    

# Show title and description.
st.title("Lab 4")
st.write(" ")
st.title("Chatbot using RAG")
st.write("The user has an option to pick which LLM they want to use for this chatbot." \
" The user is able to ask questions related to Syracuse University's data courses, "
"and if desired, can input up to two urls to give the bot context." \
" There is a 2000 token conversation memory buffer, and after 6 messages a summary of the conversation" \
"so far will be returned.")

## querying collection for testing - uncomment to test
#topic = st.sidebar.text_input('Topic', placeholder='Type your topic (e.g., GenAI)...')

#if topic:
    #client = st.session_state.openai_client
    #response = client.embeddings.create(
        #input=topic,
        #model='text-embedding-3-small'
    #)

    # get the embedding
    #query_embedding = response.data[0].embedding

    # get text related to this question (this prompt)
    #results = collection.query(
        #query_embeddings=[query_embedding],
        #n_results=3
    #)

    # display the results
    #st.subheader(f'Results for: {topic}')

    #for i in range(len(results['documents'][0])):
        #doc = results['documents'][0][i]
        #doc_id = results['ids'][0][i]

        #st.write(f'**{i+1}. {doc_id}**')
        #st.write(doc)

#else:
    #st.info('Enter a topic in the sidebar to search the collection')

# user options
st.sidebar.header("LLM Options")
llm = st.sidebar.radio("Choose LLM vendor", ("OpenAI", "Claude"))
advanced_model = st.sidebar.checkbox("Use advanced model")

if llm == "OpenAI":
    model = "gpt-4o-mini"
    if advanced_model:
        model = "gpt-4o"
else:  # Claude
    model = "claude-3-haiku-20240307"
    if advanced_model:
        st.sidebar.write("No premium model available for Claude/anthropic")

# URL inputs
st.sidebar.header("URL input")
url1 = st.sidebar.text_input("Input first url")
url2 = st.sidebar.text_input("Input second url")

# dynamic system prompt
system_prompt = ( "You are a helpful assistant. Always explain things in a simple way a 10-year-old can understand. "
"You may have access to relevant documets. Be clear when using information from these documents." ) 

if url1: 
    system_prompt += f"\n\nThe user has provided URL 1: {url1}" 
if url2: 
    system_prompt += f"\n\nThe user has provided URL 2: {url2}"

# chat history initialization
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": 
            system_prompt},
        {"role": "assistant", "content": "How can I help you?"}
    ]
else:
    st.session_state["messages"][0]["content"] = system_prompt

if "more_info" not in st.session_state:
    st.session_state.more_info = False

# summary initialization
if "summary" not in st.session_state: 
    st.session_state.summary = ""

# display chat history BEFORE input
for msg in st.session_state.messages:
    if msg["role"] != "system":  # Don't display system messages
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# chat input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    if st.session_state.more_info:
        lower = prompt.lower().strip()
        if lower == "yes":
            system_msg = st.session_state.messages[0]
            conversation = st.session_state.messages[1:]
            
            # Token buffer logic
            max_tokens = 2000
            system_tokens = len(system_msg["content"].split())
            buffer = []
            tokens_count = system_tokens
            for msg in reversed(conversation):
                msg_tokens = len(msg["content"].split())
                if tokens_count + msg_tokens > max_tokens:
                    break
                buffer.insert(0, msg)
                tokens_count += msg_tokens
            
            messages = [system_msg] + buffer
            
            # stream based on chosen llm
            if llm == "OpenAI":
                client = st.session_state.openai_client
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )
                with st.chat_message("assistant"):
                    more_info = st.write_stream(stream)
                    
            else:  # Claude
                client = st.session_state.claude_client
                system_content = system_msg["content"]
                claude_messages = [msg for msg in messages if msg["role"] != "system"]
                
                with st.chat_message("assistant"):
                    more_info = ""
                    message_placeholder = st.empty()
                    
                    with client.messages.stream(
                        model=model,
                        system=system_content,
                        messages=claude_messages,
                        max_tokens=1000
                    ) as stream:
                        for text in stream.text_stream:
                            more_info += text
                            message_placeholder.markdown(more_info + "▌")
                        message_placeholder.markdown(more_info)
            
            more_info_answer = more_info + "\n\nDo you want more info?"
            st.session_state.messages.append(
                {"role": "assistant", "content": more_info_answer}
            )
        elif lower == "no":
            reply = "What else can I help you with?"
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.more_info = False
        else:
            reply = "Please reply with Yes or No."
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        rag_context, source_files = get_rag_context(prompt)
        system_msg = st.session_state.messages[0]
        conversation = st.session_state.messages[1:]
        
        # Token buffer logic
        max_tokens = 2000
        system_tokens = len(system_msg["content"].split())
        buffer = []
        tokens_count = system_tokens
        for msg in reversed(conversation):
            msg_tokens = len(msg["content"].split())
            if tokens_count + msg_tokens > max_tokens:
                break
            buffer.insert(0, msg)
            tokens_count += msg_tokens
        
        messages = [system_msg] + buffer
        if rag_context:
            rag_prompt = f"""Please answer the question based on the provided documents.
            Document Context: {rag_context}
            User Question: {prompt}
            Please provide an answer using the document context above. Make it clear you're using information from the provided documents"""

            messages[-1] = {"role": "user", "content": rag_prompt}
        
        # stream based on chosen llm
        if llm == "OpenAI":
            client = st.session_state.openai_client
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
                
        else:  # Claude
            client = st.session_state.claude_client
            system_content = system_msg["content"]
            claude_messages = [msg for msg in messages if msg["role"] != "system"]
            
            with st.chat_message("assistant"):
                response = ""
                message_placeholder = st.empty()
                
                with client.messages.stream(
                    model=model,
                    system=system_content,
                    messages=claude_messages,
                    max_tokens=1000
                ) as stream:
                    for text in stream.text_stream:
                        response += text
                        message_placeholder.markdown(response + "▌")
                    message_placeholder.markdown(response)
        
        final_response = response + "\n\nDo you want more info?"
        st.session_state.messages.append(
            {"role": "assistant", "content": final_response}
        )
        st.session_state.more_info = True

        # generate summary after 6 messages
        if len(st.session_state.messages) > 7:

            # build conversation
            convo_text = ""
            for m in st.session_state.messages[1:]:
                if m["role"] != "system":
                    convo_text += f"{m['role']}: {m['content']}\n"

            # build summary prompt
            summary_prompt = [
                {"role": "system", "content": "Summarize the following conversation in 3–4 sentences."},
                {"role": "user", "content": convo_text}
            ]

            # generate summary with chosen llm
            if llm == "OpenAI":
                client = st.session_state.openai_client
                result = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=summary_prompt
                )
                summary_text = result.choices[0].message.content

            else:  
                client = st.session_state.claude_client
                result = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    system="Summarize the following conversation in 3–4 sentences.",
                    messages=[{"role": "user", "content": convo_text}]
                )
                summary_text = result.content[0].text

            # display summary
            with st.chat_message("assistant"):
                st.markdown(f"Conversation summary so far:\n\n{summary_text}")

            # save summary
            st.session_state.messages = [
                st.session_state.messages[0],  # keep system
                {"role": "assistant", "content": f"Summary so far:\n\n{summary_text}"}
            ]

            # store summary for system prompt memory
            st.session_state.summary = summary_text