# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install MariaDB client, netcat (for wait-for-it.sh), and other dependencies
RUN apt-get update && apt-get install -y \
    mariadb-client \
    gcc \
    libmariadb-dev \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


# Create a directory for the app
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the SQL script and the Python app to the working directory
COPY commands.sql /app/
COPY wait-for-db.sh /app/

# Make the wait-for-it script executable
RUN chmod +x /app/wait-for-db.sh

# Expose port if the app serves something (optional)
EXPOSE 8000

# Run the Streamlit app after ensuring the database is up
CMD ["/bin/bash", "-c", "./wait-for-it.sh db:3306 -- streamlit run main.py"]
