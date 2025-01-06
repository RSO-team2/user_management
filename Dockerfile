# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN ["python", "connect.py"]

# Make port 5000 available to the world outside this container
EXPOSE 80

# Define the command to run the app
CMD ["python", "app.py"]