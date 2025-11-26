FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source files
COPY . .

# Build the components
RUN npm run build

# Output stage - just the built files
FROM scratch
COPY --from=builder /app/dist /dist
