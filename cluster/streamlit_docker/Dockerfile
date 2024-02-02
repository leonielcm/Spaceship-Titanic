#Dockerfile for Streamlit app

# Base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy requirements.txt to working directory
COPY requirements.txt .

COPY client.properties .

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy app.py to working directory
COPY streamlit_titanic.py .

# Expose port 80
EXPOSE 80

# Run app.py at container launch
CMD ["streamlit", "run", "streamlit_titanic.py", "--server.port=80"]
