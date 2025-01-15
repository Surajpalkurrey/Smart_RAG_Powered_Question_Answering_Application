# Smart_RAG_Powered_Question_Answering_Application.

## Overview
This project implements a Retrieval-Augmented Generation (RAG) based application for answering user queries by processing different types of inputs, including PDF files, URLs, and web search results. The app uses a locally hosted Ollama Large Language Model (LLM) to generate context-aware answers, providing fast and reliable information retrieval. The app is built using Python, and Streamlit for the front end, and integrates Chroma for embedding-based document retrieval.

## Key Features
- *Multi-input Support*: Accepts inputs from PDFs, URLs, or web search queries.
- *Locally Hosted LLM*: Powered by Ollama's locally run LLM for faster and more secure query processing.
- *Embeddings-based Retrieval*: Utilizes Chroma to store document embeddings for efficient context retrieval and answer generation.
- *User-Friendly Interface*: Streamlit-based interface for seamless user experience and dynamic progress tracking during query processing.

## Project Structure

```
├── app.py                                        # Main application file
├── .env                                          # Environment variables file (not pushed to GitHub)
├── requirements.txt                              # Python dependencies 
├── README.md                                     # Project documentation
└── assets/                                       # Assets like screenshots, if needed
```




## Getting Started

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- Streamlit
- PyPDF2
- Langchain
- Chroma
- Google Custom Search API Key

### Installation
1. Clone the repository:
   
   git clone https://github.com/your-repo-name.git
   cd your-repo-name
2. Install the required python packages:
    pip install -r requirements.txt

3. Add your Google Custom Search API key and CX (Search Engine ID) to the environment variables.

## Usage
To run the app locally:
 streamlit run app.py
1. Upload a PDF, enter URLs, or input a search query.
2. Enter your question and click "Get Answer."
3. View the answer generated from relevant documents or web search results, powered by the Ollama LLM.
![image](https://github.com/user-attachments/assets/fa73bcad-3a31-485d-9553-c8fc8e01fddb)




## Tech Stack
- Languages: Python
- Libraries: Langchain, Streamlit, PyPDF2, Chroma
- API: Google Custom Search API
- LLM: Ollama (locally powered)

## Contributing
Feel free to submit issues, fork the project, or create pull requests to enhance functionality.

## License
This project is licensed under the MIT License.
Here’s your README formatted for GitHub, ready to be pasted directly:
