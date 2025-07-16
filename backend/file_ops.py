import os 
import shutil
import time
import gc

UPLOAD_DIRECTORY = "uploads"
VECTORSTORE_DIRECTORY ="vectorestores"


def save_uploaded_file(file_bytes: str, filename: str, max_files: int = 3) -> tuple:
    """
    Saves a PDF file if conditions are met. Returns status as a tuple.

    Returns:
        (success: bool, message: str)
    """

    # Ensure the directory exists
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Sanitize filename BEFORE checking existence
    safe_filename = filename.replace(" ", "_").replace(",", "")
    filepath = os.path.join(UPLOAD_DIRECTORY, safe_filename)

    # Create a var to store a all the files in the said directory
    files = os.listdir(UPLOAD_DIRECTORY)
    
    # Ensure the number of files in the list is less than than 3 and the file is pdf only.
    if len(files) >= max_files :
        return False, f"Total {len(files)} uploaded.\n Cannot upload more than {max_files} files."
    
    # File extension check 

    # Check if the file is already existed in the directory
    if safe_filename in files:
        return False, f"{filename} has been already loaded."
    
  
    if not filename.lower().endswith(".pdf"):
        return False, "Only PDF files are accepted"
    
    try: 
        # Create a file path, joining the directory and file name and store in the said dir. 
        # filepath = os.path.join(UPLOAD_DIRECTORY, filename.replace(" ", "_").replace(",", ""))
        with open(filepath, "wb") as f:
            f.write(file_bytes)

        # Return the success message.
        return True, f"File '{filename}' uploaded successfully!"
    # If file is different than pdf return failure message.
    except Exception as e:
        return False, f"Uploaded failed: {str(e)}"



def cleanup_uploads():
    for folder in ["uploads", "vectorestores"]:
        for file in os.listdir(folder):
            path = os.path.join(folder. file)
            if os.path.isfile(path):
                os.remove(path)



# This function assumes vectorstore is stored globally or can be accessed
def unload_vectorstore():
    global vectorstore  # or access it from wherever you store it
    try:
        if vectorstore:
            del vectorstore
            gc.collect()  # Forces release of file handles
            time.sleep(0.5)  # Optional: wait to ensure handles are released
    except NameError:
        pass  # If vectorstore wa

def delete_file(filename, upload_dir=UPLOAD_DIRECTORY, vector_dir=VECTORSTORE_DIRECTORY):
    unload_vectorstore()
    file_delete_message = ""
    folder_delete_message = ""
    file_or_folder_found = False

    
    filepath = os.path.join(upload_dir, filename)
    folderpath = os.path.join(vector_dir, filename[:-4])

    if os.path.exists(filepath):
        file_or_folder_found = True

        if os.path.isfile(filepath):
            os.remove(filepath)
            file_delete_message = f"{filename} removed from {upload_dir}."
            
    if os.path.exists(folderpath):
        file_or_folder_found = True
        if os.path.isdir(folderpath):
            shutil.rmtree(folderpath)
            folder_delete_message = f"{filename} directory removed from {vector_dir}."

    if not file_or_folder_found:
        return False, f"{filename} does not exists."
    
    return True, {
        "file_message": file_delete_message, 
        "folder_messsage": folder_delete_message
    }

    
