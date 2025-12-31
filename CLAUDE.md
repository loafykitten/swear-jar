# Swear-Jar Monorepo

A Bun-based monorepo for stream swear detection tools. The service provides a backend API with a React widget overlay, while vox is a TUI that captures microphone input for real-time speech recognition and swear detection.

## Workspaces

- **shared/** (@swear-jar/shared) - Shared TypeScript types between projects
- **service/** (@swear-jar/service) - Bun backend with API, WebSockets, and React widget
- **vox/** (@swear-jar/vox) - Ink TUI for speech recognition and swear detection

## Bun-First Development

Use Bun instead of Node.js for all operations:

- `bun install` instead of npm/yarn/pnpm install
- `bun run <script>` instead of npm run
- `bun test` instead of jest/vitest
- `bunx` instead of npx

See `service/CLAUDE.md` and `vox/CLAUDE.md` for project-specific Bun conventions.

## Commands

### From the monorepo root:

```sh
# Install all workspace dependencies
bun install

# Service commands
bun run dev:service    # Development with hot reload
bun run start:service  # Production mode
bun run test:service   # Run service tests

# Vox commands
bun run dev:vox        # Development with hot reload
bun run start:vox      # Production mode
bun run test:vox       # Run vox tests
```

### Directly in workspaces:

```sh
# In service/ or vox/
bun dev    # Development
bun start  # Production
bun test   # Tests
```

## Workspace Dependencies

To use shared types in `service` or `vox`, add to `package.json`:

```json
{
  "dependencies": {
    "@swear-jar/shared": "workspace:*"
  }
}
```

Then import:

```ts
import { SomeType } from '@swear-jar/shared'
```

## Code Style

Prettier is configured at the root (`.prettierrc`):

- Tabs (width 4)
- No semicolons
- Single quotes
- Trailing commas

## Docker

The service can be deployed via Docker:

```sh
# Build and run
docker compose up --build

# Run in background
docker compose up -d
```

Service runs on port 3000. SQLite data persists in `swear-data` volume.

## Project Documentation

For detailed conventions specific to each project:

- **service/CLAUDE.md** - Bun.serve(), SQLite, WebSockets, HTML imports, React frontend
- **vox/CLAUDE.md** - Ink TUI components, terminal rendering patterns
