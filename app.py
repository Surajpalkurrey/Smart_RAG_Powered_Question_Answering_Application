
import tempfile
import PyPDF2
import io
import streamlit as st
import requests
from langchain.docstore.document import Document
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
import os
from dotenv import load_dotenv

def web_search(query):
    """
    Perform a web search and return the top search results.
    
    Args:
        query: The search query.

    Returns:
        A list of search result snippets
    """


    # Load environment variables from .env file
    load_dotenv()

    # Access the environment variables
    api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")
    api_url=os.getenv("GOOGLE_CUSTOM_SEARCH_API_URL")

    # Use the variables in your code
    params = {
        "q": query,
        "key": api_key,
        "cx": cx,
        "gl": "IN",   # Restrict results to India
        "hl": "en"    # Set language to English (if needed)
    }


    # api_url = "https://www.googleapis.com/customsearch/v1"

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        # Extract snippets or results from the response
        snippets = [item['snippet'] for item in search_results.get('items', [])]
        return snippets

    except requests.HTTPError as e:
        print(f"HTTPError: {e}")
        return ["Error occurred during web search."]

def process_input(input_type, input_data, question):
    """
    Processes either a URL, PDF file, or performs a web search, returning the desired response.

    Args:
        input_type: The type of input (either "url", "pdf", or "search").
        input_data: The URL, PDF file content, or search query.
        question: The question to be answered.

    Returns:
        The response generated by the RAG model.
    """

    model_local = Ollama(model="mistral")

    if input_type == "url":
        # Process URL
        urls_list = input_data.split("\n")
        docs = [WebBaseLoader(url).load() for url in urls_list]
        docs_list = [item for sublist in docs for item in sublist]

        # Split the text into chunks
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=5000, chunk_overlap=50)
        doc_splits = text_splitter.split_documents(docs_list)

    elif input_type == "pdf":

        pdf_file = io.BytesIO(input_data)  # input_data is already the PDF binary data
        
        # Use PyPDF2 to extract the text
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_list = [page.extract_text() for page in pdf_reader.pages]

        docs = [Document(page_content=text) for text in text_list]

        # Split the PDF text into chunks
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=5000, chunk_overlap=50)
        doc_splits = text_splitter.split_documents(docs)
        
    elif input_type == "search":
        # Perform web search
        search_results = web_search(input_data)
        docs = [Document(page_content=result) for result in search_results]

        # Split the search results into chunks
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=5000, chunk_overlap=50)
        doc_splits = text_splitter.split_documents(docs)

    else:
        raise ValueError("Invalid input type. Must be 'url', 'pdf', or 'search'.")

    # Convert text chunks into embeddings and store in vector database
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embeddings.OllamaEmbeddings(model='nomic-embed-text')
    )
    retriever = vectorstore.as_retriever()

    # Perform the RAG
    after_rag_template = """
    You are Prashna, an expert on the topic with the following information available as context:

    {context}

    Use the information from this context to answer the following question:

    {question}

    If the context does not contain enough information to fully answer the question, acknowledge that and use your general knowledge to provide as much detail as possible based on what is available. Mention that additional information comes from your knowledge base.

    Additional Knowledge (if needed):
    """
    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    after_rag_chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | after_rag_prompt
        | model_local
        | StrOutputParser()
    )

    # Retrieve relevant documents
    relevant_docs = retriever.get_relevant_documents(question)
    
    # Create context for the prompt
    context = "\n".join(doc.page_content for doc in relevant_docs)

    # Generate the answer
    return after_rag_chain.invoke({"context": context, "question": question})

# Streamlit Interface
st.title("Advanced RAG-powered Question Answering App")

# Choose between URL, PDF, or Web Search
input_type = st.selectbox("Select Input Type", ["PDF", "URL", "Web Search"])

if input_type == "PDF":
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file is not None:
        pdf_data = uploaded_file.read()

elif input_type == "URL":
    url_input = st.text_area("Enter URLs (one per line)")

elif input_type == "Web Search":
    search_query = st.text_input("Enter your search query:")

question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if question:
        with st.spinner("Processing your request..."):
            # Initialize the progress bar with a custom status
            progress_bar = st.empty()
            progress_text = st.empty()
            progress_bar.progress(0, "Starting...")
            
            if input_type == "PDF" and uploaded_file:
                progress_text.text("Processing PDF...")
                progress_bar.progress(20, "Reading PDF content...")
                answer = process_input("pdf", pdf_data, question)
                progress_bar.progress(60, "Generating answer...")
                st.write("Answer:", answer)
                progress_bar.progress(100, "Done")

            elif input_type == "URL" and url_input:
                progress_text.text("Processing URLs...")
                progress_bar.progress(20, "Loading URLs...")
                answer = process_input("url", url_input, question)
                progress_bar.progress(60, "Generating answer...")
                st.write("Answer:", answer)
                progress_bar.progress(100, "Done")

            elif input_type == "Web Search" and search_query:
                progress_text.text("Performing web search...")
                progress_bar.progress(20, "Searching the web...")
                answer = process_input("search", search_query, question)
                progress_bar.progress(60, "Generating answer...")
                st.write("Answer:", answer)
                progress_bar.progress(100, "Done")

            else:
                st.warning("Please provide the required input (PDF, URL, or Web Search).")
                progress_bar.progress(0, "Error...")

    else:
        st.warning("Please enter a question.")
        progress_bar.progress(0, "Error...")
