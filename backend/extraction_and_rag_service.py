from backend.vectorstore_chain import load_or_create_vector_store
import utils.helper_functions as hf
import backend.schemas as sm

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

import pandas as pd

import asyncio
from utils.logger_config import setup_logger

logger = setup_logger(name="backend_log", log_file="logs/backend.log")

def extract_data(filepath: str, schema_name: str):
    # Initialize the model
    model = hf.load_openai_model(model="gpt-4o-mini")

    # load or create a vector store 
    store = asyncio.run(load_or_create_vector_store(filepath=filepath))

    # Select the schema
    if schema_name.lower() == "keydates":
        schema = sm.RFPKeyDates
    elif schema_name.lower() == "contact":
        schema = sm.RFPClientContactDetails
    elif schema_name.lower() == "submission":
        schema = sm.RFPSubmissionDetails
    elif schema_name.lower() == "procurement":
        schema = sm.RFPProcurementInformation
    elif schema_name.lower() == "project":
        schema = sm.RFPProjectInformation
    else:
        raise ValueError(f"Unknown schema name: {schema_name}")
    

    extraction_prompt = PromptTemplate( 
        input_variables = ["context"],
        template="""You are an Expert RFP / EOI paser who can extract the needfull information
                    from any RFP/EOI document efficiently and accurately.

                    🔒 Rules:
                    - Only use the provided context — do not assume or hallucinate values.
                    - If a field is not clearly stated, return `null`.
                    - Prefer values that are closest to definitions provided.
                    NOTE THAT YOU ONLY USE THE CONTEXT {context} provided to you TO ANSWER THE QUERY,

                    """
        )

    query = f"""Extract the relavant documents from a retriever to include the accurate information
                about following:
                {hf.extract_basemodel_field_and_description(schema)}
                """
    
    # Create a retriever 
    retriever = hf.create_retriever_from_store(store, k=10)
    extraction_chain = (
        retriever | 
        RunnableLambda(hf.combine_all_relevant_chunks_text) |
        extraction_prompt |
        model.bind_tools([schema])
    )

    response = extraction_chain.invoke(query)

    if response.tool_calls:
        info = response.tool_calls[0]['args']
        df = pd.DataFrame(list(info.items()), columns=["Key", "Value"])
        logger.info("Information successfully extracted!")
        return  df.to_dict('records'), [{"name": "Items", "id": "Key"}, {'name': "Value", "id": "Value"}]
    else: 
        df = pd.DataFrame([{"Error": "No relevant information found"}])
        logger.error("Extraction failed!")
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]



def run_rag(filepath, user_query):

    store = asyncio.run(load_or_create_vector_store(filepath=filepath))
    model = hf.load_openai_model()

    rag_template = PromptTemplate(
        template="""You are a helpful assistant. You answers the user query using" 
        in a very professional way and succinct way. You answer the query {user_query} using
        only form the provided context:
        {context}.
        IF YOU DONT HAVE ENOUGH CONTEXT TO ANSWER THE QUERY THEN JUST SAY 
        'I do not that enough context to answer your question.' And do not 
        assume anything. May be you can ask a followup question whenever is appropriate""",
        input_variables=['context', 'user_query']
        )
    
  
    retriever = hf.create_retriever_from_store(store, k=5)
    augment_query = RunnableParallel({
        "context": retriever | RunnableLambda(hf.combine_all_relevant_chunks_text),
        "user_query": RunnablePassthrough()

    })
            
    rag_chain = augment_query | rag_template | model | StrOutputParser()
    result = rag_chain.invoke(user_query)
    if result:
        logger.info("RAG succeded!")
    else:
        logger.error("RAG failed")

    return result
    
