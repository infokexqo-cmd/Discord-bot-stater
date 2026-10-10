# discord-bot-starter

A minimal, production-ready starter template for Discord bots built with
[discord.py](https://discordpy.readthedocs.io/) 2.x. Slash commands, cogs,
sane config, logging, and error handling — so you can skip the boilerplate
and start building features.

## Features

- **Slash commands** (`/ping`, `/serverinfo`, `/userinfo`, `/kick`, `/ban`,
  `/timeout`) implemented as cogs
- **`.env`-based config** with fail-fast validation (missing token? you get a
  clear error, not a cryptic traceback)
- **Error handling** — friendly ephemeral replies for cooldowns, missing
  permissions, and unexpected errors
- **Instant dev sync** — point `DEV_GUILD_ID` at your test server and slash
  commands appear immediately instead of waiting up to an hour
- **Structured logging** to stdout (Docker-friendly)
- **Dockerfile** included for one-command deploys

## Quickstart

**Requirements:** Python 3.10+

1. **Create a bot** at the
   [Discord Developer Portal](https://discord.com/developers/applications) →
   *New Application* → *Bot* → *Reset Token* and copy the token.
   Enable the **Server Members Intent** under *Privileged Gateway Intents*
   (needed for `/userinfo` and moderation commands).

2. **Invite the bot** to your server. In the portal: *OAuth2 → URL Generator*,
   check scopes `bot` and `applications.commands`, pick the permissions you
   need, and open the generated URL. It looks like this:

   ```
   https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot+applications.commands&permissions=8
   ```

   (`permissions=8` is Administrator — fine for your own test server; use
   least-privilege permissions in production.)

3. **Run it:**

   ```bash
   git clone https://github.com/<you>/discord-bot-starter.git
   cd discord-bot-starter
   pip install -r requirements.txt
   cp .env.example .env   # then paste your token into .env
   python bot.py
   ```

4. Type `/ping` in your server. 🎉

> Tip: set `DEV_GUILD_ID` in `.env` to your test server's ID
> (Server Settings → *Advanced* → enable *Developer Mode*, then right-click
> the server name → *Copy Server ID*). Slash commands then sync instantly
> while you develop.

## Project structure

```
discord-bot-starter/
├── bot.py            # entry point: bot class, cog loading, error handling
├── config.py         # .env parsing + validation (fails fast on bad config)
├── cogs/
│   ├── __init__.py
│   ├── general.py    # /ping, /serverinfo, /userinfo
│   └── moderation.py # /kick, /ban, /timeout (permission-gated)
├── .env.example      # copy to .env and fill in your token
├── requirements.txt  # pinned dependencies
├── Dockerfile
└── LICENSE (MIT)
```

## Adding a new cog

Create `cogs/fun.py`:

```python
import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello.")
    async def hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Hello, {interaction.user.mention}!"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
```

Then add `"cogs.fun"` to `INITIAL_COGS` in `bot.py` and restart. That's it —
the cog is loaded and its commands are synced automatically.

## Docker

```bash
# Build
docker build -t discord-bot-starter .

# Run (token passed at runtime — never baked into the image)
docker run -d --name mybot --restart unless-stopped \
  -e DISCORD_TOKEN=your-token-here \
  -e DEV_GUILD_ID=your-server-id \
  discord-bot-starter
```

Or with an env file:

```bash
docker run -d --name mybot --restart unless-stopped --env-file .env discord-bot-starter
```

## Configuration

| Variable         | Required | Default | Description                                    |
| ---------------- | -------- | ------- | ---------------------------------------------- |
| `DISCORD_TOKEN`  | yes      | —       | Bot token from the Developer Portal            |
| `COMMAND_PREFIX` | no       | `!`     | Prefix for legacy prefix commands              |
| `DEV_GUILD_ID`   | no       | —       | Test server ID for instant command sync        |
| `LOG_LEVEL`      | no       | `INFO`  | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

## Contributing

Issues and pull requests are welcome! Please:

1. Fork the repo and create a branch (`git checkout -b feature/my-cog`).
2. Keep the style consistent (type hints, docstrings, no unused imports).
3. Test your cog loads: run the bot with `DEV_GUILD_ID` set and check the
   commands appear.
4. Open a PR describing what you added and why.

## License

MIT — see [LICENSE](LICENSE).
