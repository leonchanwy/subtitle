# Base Image to use
FROM python:3.11.5

# Update system and install dependencies
RUN apt-get update && apt-get install -y gcc build-essential libffi-dev libssl-dev ffmpeg

# Upgrade pip
RUN python -m pip install --upgrade pip

# Expose port 8080
EXPOSE 8080

# Copy Requirements.txt file into app directory
COPY requirements.txt app/requirements.txt

# Install all requirements in requirements.txt
RUN pip install -r app/requirements.txt

# Copy all files in current directory into app directory
COPY . /app

# Change Working Directory to app directory
WORKDIR /app

# Run the application on port 8080
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]