# Multi-stage build: Builder stage with Python for template generation
FROM python:3.12-alpine AS builder

# Install build dependencies
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy template files
COPY templates/ ./templates/
COPY build.py .

# Build the static site
RUN python build.py

# Production stage: Nginx Alpine - ultra lightweight (~2MB base image!)
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /build/dist/ /usr/share/nginx/html/

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# nginx starts automatically
