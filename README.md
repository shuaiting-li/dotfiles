# dotfiles

Personal configuration files, primarily for [Claude Code](https://claude.com/claude-code).

## Contents

| Path | Purpose |
|------|---------|
| `claude/statusline.py` | Two-line Claude Code status line: model, directory, git branch/diff counts on line 1; context usage bar, session cost, and 5h/7d rate limits on line 2. |

## Install on a new machine

### Quick install (Claude Code can do this for you)

Paste this prompt into Claude Code on the new machine:

> Install my statusline from `https://github.com/shuaiting-li/dotfiles`. Clone the repo to `~/src/dotfiles`, copy `claude/statusline.py` to `~/.claude/statusline.py`, make it executable, and register it in `~/.claude/settings.json` under the `statusLine` key as `{"type": "command", "command": "python3 ~/.claude/statusline.py"}`. Preserve any other existing keys in `settings.json`.

### Manual install

```bash
# 1. Clone the repo
git clone https://github.com/shuaiting-li/dotfiles.git ~/src/dotfiles

# 2. Copy the statusline into place
cp ~/src/dotfiles/claude/statusline.py ~/.claude/statusline.py
chmod +x ~/.claude/statusline.py

# 3. Register it in ~/.claude/settings.json
#    Add (or merge) this key:
#    "statusLine": { "type": "command", "command": "python3 ~/.claude/statusline.py" }
```

Example minimal `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
}
```

Restart Claude Code (or open a new session) and the status line will appear at the bottom.

## Requirements

- Python 3 (uses only the standard library)
- `git` on `PATH` (optional — git info is hidden when unavailable)
- A terminal that supports ANSI colors and OSC 8 hyperlinks (most modern terminals do)

## Updating

To pull the latest version on a machine that already has it installed:

```bash
cd ~/src/dotfiles && git pull
cp claude/statusline.py ~/.claude/statusline.py
```
