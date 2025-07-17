# base image
FROM python:3.11-slim

# Set environment variables to supress prompts 
ENV DEBIAN_FRONTEND=noninteractive 

# Install poppler-utils and other system dependencies
RUN apt-get update && \
    apt-get install -y poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Workdir 
WORKDIR /app


# copy
COPY . /app

# run 
RUN pip install --no-cache-dir -r requirements.txt

# port 
EXPOSE 8000

# command
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
