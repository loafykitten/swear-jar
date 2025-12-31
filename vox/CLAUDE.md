Default to using Bun instead of Node.js.

- Use `bun <file>` instead of `node <file>` or `ts-node <file>`
- Use `bun test` instead of `jest` or `vitest`
- Use `bun install` instead of `npm install` or `yarn install` or `pnpm install`
- Use `bun run <script>` instead of `npm run <script>` or `yarn run <script>` or `pnpm run <script>`
- Use `bunx <package> <command>` instead of `npx <package> <command>`
- Bun automatically loads .env, so don't use dotenv.

## APIs

- `WebSocket` is built-in. Don't use `ws`.
- Prefer `Bun.file` over `node:fs`'s readFile/writeFile
- Bun.$`ls` instead of execa.

## Testing

Use `bun test` to run tests.

```ts#index.test.ts
import { test, expect } from "bun:test";

test("hello world", () => {
  expect(1).toBe(1);
});
```

## TUI (Terminal UI)

This is an Ink TUI application. Use Ink components instead of HTML/CSS.

**Entry point pattern:**

```ts#src/app/App.tsx
import { render, Text } from 'ink';
import React from 'react';
import { Greeting } from '../components/Greeting';

const App = () => <Greeting />;

render(<App />);
```

**Component pattern:**

```tsx#src/components/Greeting.tsx
import { Text } from 'ink';
import React from 'react';

export const Greeting = () => {
  return <Text>Hello, world!</Text>;
};
```

**Common Ink components:**
- `<Text>` - Render text with optional styling (color, bold, etc.)
- `<Box>` - Flexbox container for layout
- `<Newline>` - Add line breaks
- `<Spacer>` - Flexible space in layouts

**Running the app:**

```sh
# Development with hot reload
bun --hot ./src/index.ts

# Production
bun ./src/index.ts
```

For more information, see the Ink documentation: https://github.com/vadimdemedes/ink
