Install all these libraries to get started.
```bash
pip install pillow discord-webhook pygetwindow pydirectinput-rgx pyautogui discord
```

Jitbit is required to macro, as it will be the main recorder software to play your movements.

Install it here: https://www.jitbit.com/macro-recorder/

There are many pirated versions so you do not have to pay for a key, or you can record your own macro with other recorders such as tinytask but the performance may be different or not suitable.

## Libraries Overview

### 1. `asyncio`
- **Pre-installed**  
- **Purpose**: Manages asynchronous operations, allowing non-blocking execution of tasks.

### 2. `logging`
- **Pre-installed**  
- **Purpose**: Provides logging functionality to track events, errors, and debugging information.

### 3. `typing`
- **Pre-installed**  
- **Purpose**: Provides type hints such as `Tuple` and `Optional` to improve code readability and reliability.

### 4. `Pillow (PIL)`
- **Install**: `pip install pillow`  
- **Purpose**: Handles image processing, including screenshots and memory-based image manipulation.

### 5. `ImageGrab (Pillow)`
- **Part of Pillow**  
- **Purpose**: Captures screenshots from the screen or a specific window.

### 6. `pydirectinput`
- **Install**: `pip install pydirectinput`  
- **Purpose**: Simulates keyboard and mouse inputs without being blocked by some applications.

### 7. `ctypes`
- **Pre-installed**  
- **Purpose**: Interfaces with Windows APIs, enabling low-level system interactions.

### 8. `json`
- **Pre-installed**  
- **Purpose**: Reads and writes JSON files, typically used for configuration data.

### 9. `os`
- **Pre-installed**  
- **Purpose**: Provides system-level operations such as file and path management.

### 10. `BytesIO`
- **Pre-installed**  
- **Purpose**: Handles in-memory binary streams, useful for processing images before sending.

### 11. `discord-webhook`
- **Install**: `pip install discord-webhook`  
- **Purpose**: Sends messages and embeds to Discord via webhooks.

### 12. `pygetwindow`
- **Install**: `pip install pygetwindow`  
- **Purpose**: Gets window titles and allows interaction with application windows.

### 13. `time`
- **Pre-installed**  
- **Purpose**: Handles time-related functions such as delays and timestamps.

### 14. `discord`
- **Install**: `pip install discord`  
- **Purpose**: Provides interaction with Discord bots and API.

### 15. `datetime`
- **Pre-installed**  
- **Purpose**: Manages date and time functions for formatting timestamps.

### 16. `discord.ext.commands`
- **Part of `discord.py`**  
- **Purpose**: Provides an extension framework for creating bot commands.

### 17. `discord.app_commands`
- **Part of `discord.py`**  
- **Purpose**: Allows interaction with Discord's application commands (slash commands).

## 📌 Pixels Settings (`"Pixels"`)

Controls image detection, search precision, and anti-randomization for Deidara-only mode.

| Key                     | Type    | Description |
|-------------------------|---------|-------------|
| `color_tolerance`       | `int`   | Defines how much a color can differ from the target color before being ignored. Higher values increase leniency. |
| `pixel_radius`          | `float`   | The search radius around the target pixel. Larger values expand the detection area. |
| `search_delay`          | `int` | Time (in seconds) between each pixel search to avoid excessive CPU usage. |
| `anti_random` | `bool`  | If `true`, this will add another macro to prevent Denji / Random modifier, selecting the character you want to be chosen. |
| `anti_random_debounce`  | `int`   | Minimum time (in seconds) before anti-random actions reset. Prevents unnecessary adjustments. |
| `anti_random_delay`     | `int` | Delay (in seconds) before executing anti-random actions. |
| `anti_random_character`             | `str`   | What character you want to choose to play. Currently supports "Deidara" and "Enel". |
| `auto_update_display_scale` | `bool`  | If `true`, automatically adjusts the script's display scaling for different screen resolutions. |
| `other_clicking` | `bool`  | If `true`, this will add another macro for extra Quality Of Life things. |
| `other_clicking_delay`  | `int`   | Delay (in seconds) before executing other clicking actions. |
| `anti_purchase_prompt`     | `bool` |  If `true`, this will automatically click No if dealing with a purchase prompt, preventing purchases and blockage of buttons, Note if you have bloxstrap, [please use this to prevent accidental purchases](https://github.com/Dantezz025/Roblox-Fast-Flags?tab=readme-ov-file#disable-in-game-purchases). |
| `anti_main_menu` | `bool`  | If `true`, this will automatically click the main menu Play button to prevent AFK world from gon.exe reset. |

---

## 🌐 Webhook Settings (`"Webhook"`)

Controls webhook notifications and Discord interactions.

| Key                     | Type    | Description |
|-------------------------|---------|-------------|
| `enable_webhooks`       | `bool`  | If `true`, enables webhook notifications. |
| `screenshot_full_screen` | `bool` | If `true`, captures the entire screen instead of a specific window. |
| `send_every_minutes`    | `int`   | Interval (in minutes) between webhook messages. |
| `ping_players`          | `bool`  | If `true`, pings specified Discord users in webhook messages. |
| `player_id_to_ping`     | `list`  | List of Discord user IDs to mention when `ping_players` is `true`. |
| `discord_webhooks`      | `list`  | List of Discord webhook URLs where messages will be sent. |

---

## 🤖 Bot Settings (`"Bot"`)

Configures the Discord bot functionality.

| Key                     | Type    | Description |
|-------------------------|---------|-------------|
| `enable_bot`            | `bool`  | If `true`, enables the Discord bot. |
| `bot_token`             | `str`   | The bot's authentication token (keep this secret). |
| `whitelisted_ids`       | `list`  | List of Discord user IDs allowed to interact with the bot. |
| `command_prefixs`       | `list`  | List of command prefixes the bot recognizes (e.g., `":"`, `";"`). |

---

## ⚙️ Other Settings (`"Other"`)

Miscellaneous configurations.

| Key                     | Type    | Description |
|-------------------------|---------|-------------|
| `print_config`          | `bool`  | If `true`, prints the current configuration to the console on startup. |
