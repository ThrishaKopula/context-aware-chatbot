# Use official Node.js image
FROM node:18

# Set working directory inside the container
WORKDIR /app

# Copy all frontend files
COPY . .

# Install dependencies
RUN npm install

# Build frontend
RUN npm run build

# Expose frontend port
EXPOSE 3000

# Start the frontend
CMD ["npm", "run", "dev"]
