# Production-ready Dockerfile for Qwik (admin-ui)
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci --prefer-offline --no-audit && npm run build

# Production stage (using a lightweight static file server)
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

# Install only production dependencies (if needed for serve)
RUN npm install -g serve

EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
