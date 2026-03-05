# Development stage
FROM node:22-slim as development

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy dependency files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Development command
CMD ["pnpm", "dev"]

# Production stage
FROM node:22-alpine as builder

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy dependency files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Build application
RUN pnpm build

# Production stage
FROM node:22-alpine as production

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy everything from builder (includes node_modules with TypeScript)
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/tailwind.config.ts ./
COPY --from=builder /app/postcss.config.mjs ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
RUN chown -R nextjs:nodejs /app

# Fix pnpm store path for nextjs user
RUN mkdir -p /home/nextjs/.local/share/pnpm && \
    chown -R nextjs:nodejs /home/nextjs/.local
USER nextjs

# Expose port
EXPOSE 3000

# Production command
CMD ["pnpm", "start"]
