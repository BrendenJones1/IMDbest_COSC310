# syntax=docker/dockerfile:1

ARG NODE_VERSION=20.19-alpine
FROM node:${NODE_VERSION} AS build

WORKDIR /app

# Install deps first (better cache)
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./

# Allow overriding API base at build time
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# Serve static build with nginx
FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

