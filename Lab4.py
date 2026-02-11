import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import sys
from chromadb.config import Settings
import chromadb
from pathlib import Path
from PyPDF2 import PdfReader


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
chroma_client = chromadb.PersistentClient(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./ChromaDB_for_Lab"
    )
)
collection = chroma_client.get_or_create_collection("Lab4Collection")

# working with chromadb on streamlit community cloud
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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
        ids=file_name,
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

# Show title and description.
st.title("Lab 4")
st.write(" ")
st.title("Chatbot using RAG")
st.write("The user has an option to pick which LLM they want to use for this chatbot." \
"The user is able to ask questions, and if desired, can input up to two urls to give the bot context." \
" There is a 2000 token conversation memory buffer, and after 6 messages a summary of the conversation" \
"so far will be returned.")

## querying collection for testing
topic = st.sidebar.text_input('Topic', placeholder='Type your topic (e.g., GenAI)...')

if topic:
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=topic,
        model='text-embedding-3-small'
    )

    # get the embedding
    query_embedding = response.data[0].embedding

    # get text related to this question (this prompt)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    # display the results
    st.subheader(f'Results for: {topic}')

    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]

        st.write(f'**{i+1}. {doc_id}**')
        st.write(doc)

else:
    st.info('Enter a topic in the sidebar to search the collection')
