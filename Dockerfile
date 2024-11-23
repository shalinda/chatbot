# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Install curl
RUN apt-get update && apt-get install -y curl && apt-get clean

# Expose the port the app runs on
EXPOSE 3000

# Start the Node.js app
CMD ["npm", "start"]

