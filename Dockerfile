# Use an official Python runtime as a parent image
FROM python

# Set the working directory in the container
WORKDIR ./

# Copy the current directory contents into the container
ADD . ./

# Install dependencies
RUN pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5001

# Define the command to run the app
CMD ["python", "./api/app.py"]