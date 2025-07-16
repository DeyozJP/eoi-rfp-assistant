# base image
FROM python:3.12-slim

# Workdir 
WORKDIR /app


# copy
COPY . /app

# run 
RUN pip install -r requirements.txt

# port 
EXPOSE 8000

# command
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
