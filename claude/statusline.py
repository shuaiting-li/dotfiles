#!/usr/bin/env python3
import json, sys, os, time, subprocess, hashlib, datetime

data = json.load(sys.stdin)

# --- Colors ---
CYAN = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
DIM = '\033[2m'
RESET = '\033[0m'

def color_by_pct(pct):
    if pct >= 90: return RED
    if pct >= 70: return YELLOW
    return GREEN

# --- Fields ---
model = data['model']['display_name']
cwd = data.get('workspace', {}).get('current_dir', data.get('cwd', ''))
dir_name = os.path.basename(cwd)
pct = int(data.get('context_window', {}).get('used_percentage', 0) or 0)
cost = data.get('cost', {}).get('total_cost_usd', 0) or 0
duration_ms = data.get('cost', {}).get('total_duration_ms', 0) or 0

# --- Clickable directory (OSC 8) ---
file_uri = f"file://{cwd}"
dir_link = f"\033]8;;{file_uri}\a{dir_name}\033]8;;\a"

# --- Git (cached) ---
CACHE_FILE = '/tmp/claude-statusline-git-cache'
CACHE_TTL = 5

def cache_key():
    return hashlib.md5(cwd.encode()).hexdigest()

def read_cache():
    try:
        if not os.path.exists(CACHE_FILE):
            return None
        if time.time() - os.path.getmtime(CACHE_FILE) > CACHE_TTL:
            return None
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        entry = cache.get(cache_key())
        return entry
    except Exception:
        return None

def write_cache(entry):
    try:
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                cache = json.load(f)
        cache[cache_key()] = entry
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception:
        pass

def git_info():
    cached = read_cache()
    if cached is not None:
        return cached

    try:
        subprocess.check_output(['git', 'rev-parse', '--git-dir'],
                                cwd=cwd, stderr=subprocess.DEVNULL)
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current'], cwd=cwd, text=True,
            stderr=subprocess.DEVNULL).strip()
        staged_out = subprocess.check_output(
            ['git', 'diff', '--cached', '--numstat'], cwd=cwd, text=True,
            stderr=subprocess.DEVNULL).strip()
        modified_out = subprocess.check_output(
            ['git', 'diff', '--numstat'], cwd=cwd, text=True,
            stderr=subprocess.DEVNULL).strip()
        staged = len(staged_out.split('\n')) if staged_out else 0
        modified = len(modified_out.split('\n')) if modified_out else 0
        entry = {'branch': branch, 'staged': staged, 'modified': modified}
    except Exception:
        entry = {}

    write_cache(entry)
    return entry

git = git_info()

# --- Line 1: model, directory, git ---
parts1 = [f"{CYAN}[{model}]{RESET}", f"{dir_link}"]

if git.get('branch'):
    git_str = f"{git['branch']}"
    s, m = git.get('staged', 0), git.get('modified', 0)
    if s: git_str += f" {GREEN}+{s}{RESET}"
    if m: git_str += f" {YELLOW}~{m}{RESET}"
    parts1.append(git_str)

line1 = ' | '.join(parts1)

# --- Line 2: context bar, cost, duration, lines, rate limits ---
bar_color = color_by_pct(pct)
filled = pct * 10 // 100
bar = '\u2588' * filled + '\u2591' * (10 - filled)

parts2 = [
    f"{bar_color}{bar}{RESET} {pct}%",
    f"${cost:.2f}",
]

# Rate limits (only when available)
rate = data.get('rate_limits', {})
five_h_pct = rate.get('five_hour', {}).get('used_percentage') if rate.get('five_hour') else None
five_h_resets = rate.get('five_hour', {}).get('resets_at') if rate.get('five_hour') else None
seven_d = rate.get('seven_day', {}).get('used_percentage') if rate.get('seven_day') else None

limit_parts = []
if five_h_pct is not None:
    c = color_by_pct(five_h_pct)
    reset_str = ''
    if five_h_resets is not None:
        reset_time = datetime.datetime.fromtimestamp(five_h_resets).strftime('%H:%M')
        reset_str = f'{DIM}@{reset_time}{RESET}'
    limit_parts.append(f"5h:{c}{five_h_pct:.0f}%{RESET}{reset_str}")
if seven_d is not None:
    c = color_by_pct(seven_d)
    limit_parts.append(f"7d:{c}{seven_d:.0f}%{RESET}")
if limit_parts:
    parts2.append(' '.join(limit_parts))

line2 = ' | '.join(parts2)

print(line1)
print(line2)
