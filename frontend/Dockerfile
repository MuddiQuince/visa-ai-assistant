FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies - we use --legacy-peer-deps to ignore version conflicts
RUN npm install --legacy-peer-deps

# Copy the rest of the code
COPY . .

# Set environment variables so Next.js knows where the backend is during build
ENV NEXT_PUBLIC_API_URL=http://localhost:5000
ENV NEXT_TELEMETRY_DISABLED 1

# Run the build
RUN npm run build

EXPOSE 3000

# Start the application
CMD ["npm", "start"]