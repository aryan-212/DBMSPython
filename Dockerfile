# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install MariaDB client and other dependencies
RUN apt-get update && apt-get install -y \
    mariadb-client \
    gcc \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for the app
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the SQL script and the Python app to the working directory
COPY App.py /app/
COPY commands.sql /app/

# Expose port if the app serves something (optional)
EXPOSE 8000

# Run the Python application
CMD ["python", "App.py"]
