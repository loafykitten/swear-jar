# Swear-Jar

A Bun-based monorepo for stream swear detection tools.

## Install

```sh
bun install
```

## Environment Variables

`.env.development` contains default variables for local development. For production (Docker or public-facing), create a `.env` file with your own `API_KEY`.

> **Security Note**: The `.env.development` API key is publicly known. Only use it for local development where no one else can connect. For production or public use, generate your own key in `.env`.

You can also swap out the `.env.development` key for local use with `bun dev:service`.

## Commands

Run from the root directory:

```sh
bun dev:service    # Development mode
bun start:service  # Production mode
bun start:vox      # Run Vox TUI
```

## Quick Start

### 1. Start the Server

```sh
# Option A: Docker
docker compose up --build -d

# Option B: Local development
bun dev:service
```

Verify the last few characters of the API key match what you expect.

### 2. Add the Widget to OBS

Add a **Browser Source** in OBS with a URL like:

```
http://localhost:3000/api/swears?pricePerSwear=0.25&maxCost=50&isAnimated=true&apiKey=<api_key>
```

Replace `<api_key>` with:
- The key from `.env.development` if using `bun dev:service`
- The key from `.env` if using Docker or `bun start:service`

| Parameter | Description |
|-----------|-------------|
| `pricePerSwear` | Cost per swear detected |
| `maxCost` | Maximum total to display |
| `isAnimated` | Fades widget after 8 seconds of inactivity |
| `apiKey` | Your API key |

### 3. Run Vox (Optional)

If you want live speech recognition and swear detection:

```sh
bun start:vox
```

### 4. Configure Vox

The config menu opens automatically. If not, press `c`.

You can use mouse or keyboard (`Tab`/`Shift+Tab`/`Enter`) to navigate.

| Setting | Notes |
|---------|-------|
| **Audio Device** | Select your microphone. Channel 1 is usually fine. |
| **Model Size** | `base` (default) works for most. `tiny` = faster, `small` = more accurate. `medium`/`large` need more resources. |
| **Base URL** | `http://localhost:3000` for local dev/Docker, or your hosted URL. |
| **API Key** | Must match the key in `.env.development` or `.env` that the server is using. |

Vox config is stored in `~/.config/vox`.

### 5. Start Recording

On the main Vox screen, press `Space` to begin recording and transcribing audio.
