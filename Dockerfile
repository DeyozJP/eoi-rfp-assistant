# base image
FROM python:3.11-slim

# Workdir 
WORKDIR /app


# copy
COPY . /app

# run 
RUN pip install -r requirements.txt

# port 
ENV PORT=8000

# command
CMD uvicorn backend.api:app --host 0.0.0.0 --port $PORT
