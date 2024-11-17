# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install AWS CLI (requires curl and unzip)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws/

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies from requirements.txt, if you have any
# In case there's no requirements.txt, you can skip this command or create one
RUN pip install --no-cache-dir -r requirements.txt || true

# Expose port 3001 to the outside world
EXPOSE 3001

# Run the app using Gunicorn with 4 worker processes
CMD ["gunicorn", "--bind", "0.0.0.0:3001", "wsgi:app", "--workers=4"]


