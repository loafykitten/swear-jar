# Monorepo-aware Dockerfile for swear-jar service
# Build from repo root: docker build -f service/Dockerfile .
FROM oven/bun:1 AS base
WORKDIR /app

# Copy workspace structure for dependency resolution
FROM base AS install
COPY service/package.json service/bun.lock ./

# Install workspace dependencies
RUN bun install --frozen-lockfile

# Copy source and run tests
FROM base AS prerelease
COPY --from=install /app/node_modules ./node_modules
COPY service ./service

# Run tests from service directory
WORKDIR /app/service
RUN NODE_ENV=test bun test

# Production image
FROM oven/bun:1-slim AS release
WORKDIR /app
ENV NODE_ENV=production

COPY --from=install --chown=bun:bun /app/node_modules ./node_modules
COPY --from=prerelease --chown=bun:bun /app/service ./service

# Create writable data directory for sqlite
RUN mkdir -p /data && chown bun:bun /data

WORKDIR /app/service
USER bun
EXPOSE 3000/tcp
ENTRYPOINT ["bun", "run", "src/index.ts"]
