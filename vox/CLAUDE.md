# Vox - Python/Textual TUI

A Terminal User Interface (TUI) for speech recognition and swear detection, built with Python and Textual.

## Architecture

- **Language**: Python 3.10+
- **TUI Framework**: [Textual](https://textual.textualize.io/) - A modern Python TUI framework with CSS-like styling
- **Dependency Management**: [uv](https://github.com/astral-sh/uv) - Fast Python package installer

## Development Setup

### First Time Setup

```bash
# Navigate to vox directory
cd vox

# Create virtual environment
uv venv

# Install dependencies (including textual)
uv pip install -e .
```

### Activate Virtual Environment

```bash
# Activate the virtual environment
source .venv/bin/activate

# Or run commands directly with uv
uv run python src/main.py
```

### Running the App

```bash
# With activated venv
python src/main.py

# Without activating venv
uv run python src/main.py
```

## Textual Development Patterns

### Component Structure

Textual uses an App-based architecture with composable widgets:

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button

class MyApp(App):
    """Main application class"""

    CSS = """
    Screen { align: center middle; }
    Button { margin: 1; }
    """

    def compose(self) -> ComposeResult:
        """Compose the UI"""
        yield Header()
        yield Button("Click me")
        yield Footer()

    def on_button_pressed(self) -> None:
        """Handle button press events"""
        self.notify("Button pressed!")
```

### Styling with CSS

Textual uses CSS-like syntax for styling widgets:

```python
CSS = """
Screen {
    align: center middle;
    background: $surface;
}

.title {
    color: $accent;
    text-style: bold;
}
"""
```

### Event Handling

Handle events using `on_*` methods:

```python
def on_key(self, event: events.Key) -> None:
    """Handle key press events"""
    if event.key == "q":
        self.exit()
```

### Reactive State

Use reactive properties for state management:

```python
from textual.reactive import reactive

class Counter(Widget):
    count = reactive(0)

    def watch_count(self, count: int) -> None:
        """Called when count changes"""
        self.update(f"Count: {count}")
```

## Project Structure

```
vox/
├── src/
│   └── main.py          # Main application entry point
├── pyproject.toml       # Project metadata and dependencies
├── README.md            # Project overview
├── .gitignore           # Git ignore patterns
└── .venv/               # Virtual environment (not in git)
```

## Dependencies

Core dependencies (defined in `pyproject.toml`):
- `textual>=0.50.0` - TUI framework

Development dependencies:
- `pytest>=7.4.0` - Testing framework

## Adding Dependencies

```bash
# Add runtime dependency
uv pip install <package>
# Then update pyproject.toml manually

# Add dev dependency
uv pip install --dev <package>
# Then update pyproject.toml under [project.optional-dependencies]
```

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

## Textual Developer Tools

Textual includes a dev console for debugging:

```bash
# Run with dev tools
textual console

# In another terminal, run your app
uv run python src/main.py
```

## Debugging in Textual

**IMPORTANT**: `print()` does NOT work inside Textual apps. Textual takes over the terminal, so any `print()` statements inside the app (screens, widgets, etc.) will not be visible.

For debugging inside the running app:
- Use `self.notify("debug message")` to show toast notifications
- Use the `textual console` dev tools (see above)
- Use logging to a file

```python
# Works BEFORE app.run() is called
print("This will show in terminal")

# Inside the app - use notify instead
def some_method(self):
    # print("This won't show!")  # DON'T DO THIS
    self.notify(f"Debug: value={some_value}")  # DO THIS
```

## Textual Screen Lifecycle

Screen lifecycle methods:
- `__init__` - Called once when screen is first created
- `compose` - Called once to build the widget tree
- `on_mount` - Called once when screen is first mounted to the DOM
- `on_show` - Called EVERY time the screen becomes visible

**IMPORTANT**: If you register a screen in the `SCREENS` dict, Textual caches the instance. Use `on_show` (not `on_mount`) to refresh data each time the screen is displayed.

```python
# BAD - only runs once if screen is cached
def on_mount(self) -> None:
    self._load_config()

# GOOD - runs every time screen is shown
def on_show(self) -> None:
    self._load_config()
```

## Textual Select Widget Gotchas

The `Select.set_options()` method resets the selection. If you need to update options AND set a value, use `call_after_refresh` to defer the value assignment:

```python
def _update_select(self) -> None:
    select = self.query_one('#my-select', Select)
    select.set_options(new_options)
    # DON'T set value here - set_options resets it
    self.call_after_refresh(self._set_select_value)

def _set_select_value(self) -> None:
    self.query_one('#my-select', Select).value = self.current_value
```

## Common Commands

```bash
# Activate venv
source .venv/bin/activate

# Run app
uv run python src/main.py

# Format code (if black is installed)
black src/

# Type check (if mypy is installed)
mypy src/

# Run tests
pytest
```

## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Textual Widget Gallery](https://textual.textualize.io/widget_gallery/)
- [Textual CSS Reference](https://textual.textualize.io/styles/)
- [uv Documentation](https://github.com/astral-sh/uv)
