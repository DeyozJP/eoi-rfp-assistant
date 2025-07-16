from utils.helper_functions import (
    load_pdf_content, 
    split_text, 
    convert_numbered_headers_to_markdown,
    vector_store
    )
from langchain_core.runnables import RunnableLambda
from utils.logger_config import setup_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from functools import partial
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from utils.helper_functions import load_config

import os

logger = setup_logger(name="backend_log", log_file="logs/backend.log")

def vector_store_chain(filepath: str, splitter_type=RecursiveCharacterTextSplitter):
    """
    Creates a LangChain-compatible processing pipeline to convert a PDF into a vector store for semantic search.

    This function dynamically builds a chain of operations that includes:
        1. Loading the content from a PDF file.
        2. (Optional) Preprocessing text to convert numbered headers to Markdown, if using MarkdownHeaderTextSplitter.
        3. Splitting the text into chunks using the specified text splitter.
        4. Creating a vector store from the resulting chunks.

    The chain adapts its behavior based on the provided `splitter_type`. If the `MarkdownHeaderTextSplitter` is used,
    it includes an additional preprocessing step to format headers as Markdown. Otherwise, it skips that step.

    Parameters:
        filepath (str): Path to the PDF file to be processed.
        splitter_type (type, optional): Text splitter class to use. Defaults to RecursiveCharacterTextSplitter.

    Returns:
        RunnableSequence: A LangChain-compatible chain for processing the PDF into a vector store.
    """

    # Create Runnable to make a text_split_chain
    r_pdf_loader = RunnableLambda(load_pdf_content)

    if splitter_type == MarkdownHeaderTextSplitter:
        r_process_text = RunnableLambda(convert_numbered_headers_to_markdown) # Format the text of pdf in markup headings.
        # As split_text function takes arguments so before passing the function to RunnableLambda, it is required to call with the arguments. 
        split_with_chunks = partial(split_text, splitter_type=splitter_type) 
        r_split_text = RunnableLambda(lambda text: split_with_chunks(text))

        vector_store_with_filepath = partial(vector_store, filepath=filepath)
        r_vector_store = RunnableLambda(lambda chunks: vector_store_with_filepath(chunks))

        vector_store_chain = (
            r_pdf_loader | 
            r_process_text | 
            r_split_text |
            r_vector_store 
            )
        
        return vector_store_chain
    
    split_with_chunks = partial(split_text, splitter_type=splitter_type) 
    r_split_text = RunnableLambda(lambda text: split_with_chunks(text))

    vector_store_with_filepath = partial(vector_store, filepath=filepath)
    r_vector_store = RunnableLambda(lambda chunks: vector_store_with_filepath(chunks))

    vector_store_chain = (
        r_pdf_loader | 
        r_split_text |
        r_vector_store 
        )
        
    return vector_store_chain
    

def vectorstore_exists(persist_path: str) ->bool:
    """ Check if the vector store already exists at the given path."""
    
    return os.path.exists(os.path.join(persist_path, "chroma.sqlite3"))


async def load_or_create_vector_store(filepath, 
                                      vectorstore_dir="vectorestores",  
                                      embedding_model: str = "text-embedding-3-large") -> Chroma:
    """
    Loads an existing vector store from disk or creates a new one from the given PDF file.

    This function first checks whether a vector store already exists for the given `filepath`. If it does,
    it loads the Chroma vector store using the specified embedding model. If not, it builds a new vector store
    by processing the PDF using a LangChain-based pipeline (`vector_store_chain`) and persists it to disk.

    Parameters:
        filepath (str): Path to the PDF document.
        vectorstore_dir (str): Directory to store or look for existing vector stores. Default is "vectorestores".
        embedding_model (str): Name of the OpenAI embedding model to use. Default is "text-embedding-3-large".

    Returns:
        Chroma: A `Chroma` vector store instance loaded from or created at the specified path.
    """

    # Check if if the vector store already exists.
    logger.info(f"filepath is: {filepath}")
    

    filename = os.path.basename(filepath).replace(".pdf", "").replace(" ", "_") # eg. "D:\Projects\RFPs\rfp.pdf" => "rfp"
    persist_path = os.path.join(vectorstore_dir, filename)
    logger.info(f"persist_path is: {persist_path}")

    try:
        if vectorstore_exists(persist_path):
            logger.info(f"Loading existing vector store from {persist_path}")
            return Chroma(
                persist_directory=persist_path,
                embedding_function=OpenAIEmbeddings(model=embedding_model, api_key=load_config()),
                collection_name="project_rfp"
            )

        else:
            logger.info(f"Creating a new vector store for {filepath} at {persist_path}")
            store = await vector_store_chain(filepath).ainvoke(filepath)
            
            return store
    except Exception as e:
        logger.error(f"error loading or creating vector store: {str(e)}")
        raise RuntimeError(f"Error loading or creating vector store, {str(e)}")
        

