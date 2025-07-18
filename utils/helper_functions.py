import re

import logging
import os
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
from langchain_openai import ChatOpenAI
from typing import List, Type, Union
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

import pdfplumber 
from pdf2image import convert_from_path 
import pytesseract
from utils.logger_config import setup_logger

logger= setup_logger(name="helper_logs", log_file="logs/helper_function.log")

def load_config(api_key="OPENAI_API_KEY"):
    """Loads the specified API KEY from the environment variables."""

    load_dotenv()
    key = os.getenv(api_key)
    if not key:
        raise EnvironmentError(f"Key  not found in the environment variables.")
    
    return key


def load_openai_model(model="gpt-4o-mini"):
    """Loads the OpenAI model with the specified openai model name and API key."""
    try:
        api_key = load_config("OPENAI_API_KEY")
        llm = ChatOpenAI(model=model,
                        temperature=0.1, openai_api_key=api_key)
        
        logger.info("LLM is loaded and it is started")
        return llm

    except Exception as e:
        logger.error(f"LLM is not configured correctly, see the error below:\n{e.args}")
        raise

    
UPLOAD_DIRECTORY = "uploads"

async def load_pdf_content(filename, dir=UPLOAD_DIRECTORY, dpi=200):
    """
    Extracts all readable text from a PDF, including:
    - Native text 
    - Tables 
    - Images or scanned content (via OCR)

    Args:
        filename (str) : a name or path of the pdf file
        dir (str) : a directory that contains the pdf file 
        dpi (int): resolution for pdf2image rendering. Default : 300

    Returns:
        str: All extracted text from the document.
    """

    logging.getLogger('pdfminer').setLevel(logging.ERROR)
    full_text = ""
    filepath = os.path.join(dir, filename)

    try:
        # Load all page images once for OCR 
        images = convert_from_path(filepath, dpi=dpi, poppler_path="/usr/bin")

        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = ""
                
                tables = page.extract_tables()
                if tables:
                    for table_ind, table in enumerate(tables):
                        # table_text = f"\n[Page {i+1} - Table {table_ind + 1}]: \n"
                        # full_text += table_text

                        for row_ind, row in enumerate(table):
                                table_text = " | ".join(cell or "" for cell in row)
        
                            # if row_ind == 0:
                            #     header_text = f"Table_{table_ind+1}_header ----- " + " | ".join(cell or "" for cell in row) + "\n"
                            #     full_text += header_text
                            # else:
                            #     body_row_text = f"Table_{table_ind+1}_content ----" + " | ".join(cell or  "" for cell in row) + "\n"
    
                                full_text += table_text

                # Extract normal text 
                text = page.extract_text()
                if text :
                    page_text += text.strip() 
                    full_text += text

                
                # # Extaract and format table 
                # tables = page.extract_tables()
                # if tables:
                #     for table_index, table in enumerate(tables):
                #         if not table or not any(table):
                #             continue
                #         table_text +=f"\n]Table {table_index + 1}]\n"

                #         # Clean adn format as markdown 

                #         for row_num, row in enumerate(table):
                #             clean_row = [" " if cell is None else str(cell).strip() for cell in row]
                #             table_text += "| " +  " | ".join(clean_row) + " |\n"

                #             if row_num == 0: 
                #                 table_text += "| " + " | ".join("---" for _ in clean_row) + " |\n"

                        

                # If no text found, use OCR 
                if not page_text.strip() or len(page_text.strip().split()) <= 3:
                    ocr_text = pytesseract.image_to_string(images[i])
                    page_text += f"\n[Page {i + 1}]\n"
                    page_text += ocr_text.strip()

                    full_text += page_text


               

        return full_text.strip()

    except Exception as e:
        raise RuntimeError(f"Error while extracting PDF content: {e}")



def is_likely_section_header(line: str) -> bool:
    """Determines whether a line is likely a section header using a specified """
    
    line = line.strip()
    pattern1 = r"^\d+\.?\s+[A-Z][A-Z\s&()\-,:]+$" 
    # pattern2 = r"^Section\s+\d+[:\-\.]\s+.+"
 
    return bool (re.match(pattern1, line))

  
def normalize_text(text: str) -> str:
    """Normalizes the text by removing extra spaces, converting to lowercase"""
    
    return re.sub(r"\s+", " ", text).strip().lower()

def convert_numbered_headers_to_markdown(text: str) -> str:
    """Checks if the line of a text is a main section header and converts the numbered or lettered
    part of the heading to a '#` markdown header.
    for example: A. Heading => # Heading
    1.2.3 Heading => # Heading

    parameter:
    text (str): the input text
    """
    
    lines = text.splitlines()
    markdown_lines = []
    i = 0

    while i < len(lines):
        current_line = lines[i].strip()

        # Checks if the line is section heas that starts with a number
        if is_likely_section_header(current_line):
            markdown_header = re.sub(r"^\d+\.?", "#", current_line)
            markdown_lines.append(f"{markdown_header}\n")
            i += 1
            continue


        # Check if the line is a letter header (e.g., "A. Heading")
        match = re.match(r"^[A-Z]\.\s+(.*)", current_line)
        # has_letter_header = bool(match)
        heading_main = match.group(1).strip() if match else current_line

        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
        next_next_line = lines[i + 2].strip() if i + 2 < len(lines) else ""

        # Try combinations of lines
        line_1_norm = normalize_text(heading_main)
        line_2_norm = normalize_text(next_line)
        line_3_norm = normalize_text(next_next_line)

        combined_1_2 = normalize_text(f"{heading_main} {next_line}")
        combined_1_2_3 = normalize_text(f"{heading_main} {next_line} {next_next_line}")

        # If any combination matches a later line (i.e., repetition)
        if line_1_norm == line_2_norm or \
           combined_1_2 == line_3_norm or \
           combined_1_2_3 == line_3_norm:
            markdown_lines.append(f"# {current_line} {next_line}".strip() + "\n")
            i += 3
            continue

        markdown_lines.append(current_line)
        i += 1

    return "\n".join(markdown_lines)




def combine_all_relevant_chunks_text(retrieved_chunks):
    """
    Combine the content of retrieved document chunks into a single string.

    This function takes a list of document objects (typically returned by a retriever),
    extracts their `page_content`, and joins them together with double newlines.
    This helps preserve logical separation between chunks while forming a unified text block.

    Parameters:
        retrieved_chunks (List[Document]): A list of document objects, each containing a `page_content` attribute.

    Returns:
        str: A single string combining the content of all retrieved chunks.
    """
    # for ind, chunk in enumerate(retrieved_chunks):

    #     print(f"Retrieved Chunk {ind+1}: \n {chunk.page_content}....\n\n")

    combined_text = "\n\n".join([document.page_content for document in retrieved_chunks ])

    return combined_text


def split_text(
        text: str, 
        splitter_type: Union[Type[RecursiveCharacterTextSplitter], 
                            Type[MarkdownHeaderTextSplitter]] = 
                            RecursiveCharacterTextSplitter,
        chunk_size=5000,
        chunk_overlap=200) -> List[Document | str]:
    """
    Splits a given text into smaller chunks using a specified text splitter.

    This function supports two types of splitters from LangChain:
    - RecursiveCharacterTextSplitter (default): Splits text into overlapping character-based chunks.
    - MarkdownHeaderTextSplitter: Splits text based on markdown header structure.

    Parameters:
        text (str): The input text to be split.
        spliter_type (Union[RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter], optional):
            The splitting strategy to use. Defaults to RecursiveCharacterTextSplitter.
        chunk_size (int, optional): The maximum size of each chunk (applicable to RecursiveCharacterTextSplitter). Defaults to 5000.
        chunk_overlap (int, optional): Number of overlapping characters between chunks (applicable to RecursiveCharacterTextSplitter). Defaults to 200.

    Returns:
        List[str | Documents]: A list of text chunks  or document objects resulting from the specified splitting strategy.
    """
    
    if splitter_type == RecursiveCharacterTextSplitter:
        # Initialize RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        chunks = text_splitter.split_text(text)

        if not chunks:
            return []
        
        # Add first 500 chars firm first chunk to all the other chunks
        prefix = chunks[0][:500]

        documents = [Document(page_content=chunks[0])]

        # Add prefix to remaining chunks 
        for chunk in chunks[1:]:
            documents.append(Document(page_content=prefix + chunk))
            
    elif splitter_type == MarkdownHeaderTextSplitter:
        # Initialize MarkdownHeaderTextSplitter
        text_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "section")]
        )

        chunks = text_splitter.split_text(text)
        if not chunks:
            return []
        
        prefix = chunks[0].page_content[:500]

        documents = [chunks[0]]

        for chunk in chunks[1:]:
            new_content = prefix + chunk.page_content
            documents.append(Document(page_content=new_content, metadata=chunk.metadata))
        

    else:
        raise ValueError("Unsupported splitter type: Use RecursiveCharacterTextSplitter or MarkdownHeaderTextSplitter")

    # for debugging
    print(f"The return type of splitter is: {type(chunks[0])}")
    

    # for debugging 
    logger.info(f"Total chunks: {len(documents)}")
    # for ind, doc  in enumerate(documents):
    #     print(f"This is chunk: {ind+1}: \n {doc.page_content}\n\n")

    return documents

    

def vector_store(
        chunks: List[Document], 
        filepath: str,
        persist_directory: str = "vectorestores",
        collections_name: str = "project_rfp",
        embedding_model: str = "text-embedding-3-large") -> Chroma:
    
    """
    Creates a Chroma vector store from provided document chunks and returns a vector store object.

    This function:
    - Embeds the document chunks using OpenAI's `text-embedding-3-large` model.
    - Stores them in a Chroma vector database (persisted to disk)..

    Parameters:
        chunks (List[Document]): The list of document chunks to index.
        filepath: A full path, where the file is located.
        persist_directory (str): Directory path where the Chroma DB will be persisted.
        collection_name (str): Name of the collection in the Chroma store.
        model (str): A valid name of a embedding model.

    Returns:
        vector store object
    """

    filename = os.path.basename(filepath).replace(".pdf", "").replace(" ", "_")

    os.makedirs(persist_directory, exist_ok=True)
    
    persist_path = os.path.join(persist_directory, filename)
    os.makedirs(persist_path, exist_ok=True)

    
    logger.info(f"Creating new vector store at {persist_path}")
    
    
    # Define and embedding model and attached to the vector store.
    embeddings = OpenAIEmbeddings(model=embedding_model, api_key=load_config())
    vector_store = Chroma.from_documents( # Since vector store is persiting from document, use from_document
        embedding=embeddings,
        documents=chunks,
        persist_directory=persist_path,
        collection_name=collections_name
        )
    
    return vector_store



def create_retriever_from_store(vector_store, k: int = 4) -> BaseRetriever:
    """
    Creates and returns a retriever object from the provided vector store using Maximal Marginal Relevance (MMR) search.

    Parameters:
        vector_store (VectorStore): The vector store instance to convert into a retriever.
        k (int, optional): The number of top documents to retrieve. Defaults to 4.

    Returns:
        BaseRetriever: A retriever object configured to use MMR-based semantic search with the specified number of results.
    """
   
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k}
        )
    return retriever


def extract_basemodel_field_and_description(class_name):
    """ Extracts field names and their descriptions from a Pydantic BaseModel class."""

    field_name_and_description = []
    for name, field in class_name.model_fields.items():

        # Use markdows-style for clarity
        field_name_and_description.append(f"**{name}**: {field.description.strip()if field.description else field.description}")

    return "\n\n".join(field_name_and_description)





