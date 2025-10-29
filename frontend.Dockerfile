# Frontend Dockerfile for development
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY ui/package*.json ./
RUN npm ci

# Copy source code
COPY ui/ ./

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]