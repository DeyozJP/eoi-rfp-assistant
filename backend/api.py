from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.extraction_and_rag_service import extract_data, run_rag
from backend.file_ops import save_uploaded_file, delete_file

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware 
from ui import create_dash_app
import uvicorn
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount Dash app 
dash_app = create_dash_app()
app.mount("/rag", WSGIMiddleware(dash_app.server))


@app.get("/")
def read_root():
    return {"message": "FastAPI root is up"}



# Create a upload endpoint
@app.post("/upload-pdf/")
async def upload_via_api(file: UploadFile = File(...)):
    file_bytes = await file.read()
    try:
        success, message = save_uploaded_file(file_bytes, file.filename)
        if not success:
            # return 409 for know issue
            raise HTTPException(status_code=409, detail=message)
        return {"success": success, "message": message}
    except HTTPException as he:
        raise he     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")




# Create extraction endpoint
@app.get("/extract-data/")
def extract_data_endpoint(filepath: str, schema_name:str):
    try:
        rows, cols = extract_data(filepath, schema_name)
        if not rows and cols:
            raise HTTPException(status_code=204, detail="No Relevant information found.")
        
        return {"rows": rows, "cols": cols}
    
    except HTTPException as he:
        raise he
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(ve)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    
# Create rag endpoint 
@app.get("/query-document/")
def query_document_endpoint(filepath: str, query: str):
    try:
        answer = run_rag(filepath, query)
        if not answer:
            raise HTTPException(status_code=204, detail="No relavant information found")
        return {"answer": str(answer)}
    
    except HTTPException as he:
        raise he
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
        
    
# Create delete endpoint 
@app.delete(("/delete-file/{filename}"))
def delete_file_endpoint(filename: str):
    try:
        is_file_deleted, messages = delete_file(filename)

        if is_file_deleted:
            return messages
        
        else:
            raise HTTPException(status_code=404, detail="File not found.")
        
    except HTTPException as he:
        raise he
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)