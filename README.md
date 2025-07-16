# EOI RFP Assistant 
A document intelligent assistant, built with FASTAPI, Langchain and  Dash to help analyze and extracts information from public procurement document such as Expression of Interest (EOI) or Request for Propsals (RFPs).

## Key Features

- Upload and Parse PDF EOIs and RFPS or any related documents
- Extract predefined structured data from EOI/RFPs
- Download the extracted data in csv for further use. 
- Ask question about documents using natural language and get accurate, context-aware anaswers.
- Update or refine the extarcted information as needed
- Simple and intuitive UI and file upload support
- Seamlessly interact with upto 3 documents cuncurrently. 


## Tech Stack 

- **Backend**: Python, FastAPI, Uvicorn
- **LLM Tools and Framework**: Langchain, OpenAI gpt-4o-mini, ChromaDB
- **UI**: Dash 
- **Dockerized** for deployment


## Setup Instructions 
Follow these steps to get the project up and running locally:

### Clone the repository 

git clone https://github.com/your-username/your-repo.git
cd your-repo 

### Create and activate a virtual environment 

python -m venv venv

venv\Scripts\activate 

###. Install Dependencies 

pip install -r requirements.txt 

### Run the application  
univorn backend.api:app --host 0.0.0.0 --port 8000 --reload

### Access the app 
Open your browser and go to http://localhost:8000 
 - to access the FASTAPI swagger (document) go to http://localhost:8000/docs
 - to access the app via UI fo to http://localhost:8000/rag

## Run with Docker 

docker build -t eoiassistant
docker run -p 8888:8000 eoiassistant


## Project Stucture 
<pre> ```plaintext project/ ├── backend/ │ ├── api.py # Main FastAPI app (Dash app is mounted here) │ ├── file_ops.py # Functions to handle file upload, deletion, etc. │ ├── extraction_and_rag_service.py # Core logic for extraction and RAG pipelines │ ├── schemas.py # Pydantic BaseModel classes for data structure │ └── vectorstore_chain.py # Logic to create and manage vector stores ├── utils/ │ ├── helper_functions.py # General utility functions │ ├── logger_config.py # Logging configuration │ └── mathjax_utils.py # Utility to format output using MathJax ├── uploads/ # Uploaded PDF files (ignored by Git) ├── vectorestores/ # Generated vector stores (ignored by Git) ├── assets/ # Static assets like images and styles ├── ui.py # Dash UI code ├── requirements.txt # Python dependencies ├── Dockerfile # Docker build instructions └── README.md # Project documentation ``` </pre>

## Author 
Deyoz Rayamajhi
