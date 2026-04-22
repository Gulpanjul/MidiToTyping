# Claude Code Token Audit — Portable Installation Recipe

**What this is:** A self-contained recipe that installs a `/token-audit`
slash command into any Claude Code workspace. The command measures real
token consumption (session-start baseline + per-session usage parsed
from Claude Code's own JSONL transcripts) and produces a ranked
optimization report.

**Origin:** Built by Ea (AI companion in the `vivi — Virtual Virtuoso`
workspace) for Yoza Wiratama at Lam Seng Hang on 2026-04-15, in
response to *"why is my Claude Code context filling so fast?"*.
The tool is portable by design — no hardcoded paths, no vivi-specific
dependencies.

**How to use this file:**

1. **Human:** Share this file to your teammate. Tell them to open their
   Claude Code, drop this file into their workspace, and say to their
   AI: *"Read CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md and install the
   `/token-audit` command following the instructions for the AI."*
2. **AI:** Read everything below and execute the "INSTRUCTIONS FOR THE AI"
   section. No need to consult other files. Everything you need is in
   this document.

---

## INSTRUCTIONS FOR THE AI (Claude Code reading this file)

You are being asked to install a `/token-audit` slash command into
the current Claude Code workspace. Follow these steps exactly.

### Step 1: Detect workspace type

Check if the current workspace is a **vivi** workspace:

```bash
test -f paths.py && test -d system/cortex/tools && echo "vivi" || echo "generic"
```

- **vivi** → use vivi file locations (Path Map A below)
- **generic** → use generic file locations (Path Map B below)

### Step 2: Choose file locations

**Path Map A — vivi workspace:**
- Python tool → `system/cortex/tools/token_audit.py`
- Command workflow → `system/cortex/commands/token-audit.md`
- Slash wrapper → `.claude/commands/token-audit.md`

**Path Map B — generic Claude Code workspace:**
- Python tool → `.claude/tools/token_audit.py` (create `.claude/tools/`
  if it does not exist)
- Slash wrapper → `.claude/commands/token-audit.md`
- No separate command workflow file — use the simpler wrapper in
  "FILE 3 — Generic slash wrapper" below, which inlines the workflow.

### Step 3: Create the files

Copy the contents of the code blocks below verbatim into the chosen
locations. **Do not modify the Python source code.** You may adapt
the command workflow markdown to match local conventions if needed
(e.g. language, author attribution).

### Step 4: Verify the installation

Run the tool to confirm it works:

```bash
# For vivi:
python system/cortex/tools/token_audit.py --text --days 14 --top 5

# For generic:
python .claude/tools/token_audit.py --text --days 14 --top 5
```

Expected outcome:
- Tool prints a "CLAUDE CODE - TOKEN AUDIT REPORT" block
- "Session Start Baseline" section shows CLAUDE.md bytes/tokens
- "Real Usage" section shows N sessions scanned (>0 if the user has
  used Claude Code in this workspace before)
- If `Sessions scanned: 0`, check the "Troubleshooting" section below.

### Step 5: Confirm the slash command is registered

Claude Code auto-registers files in `.claude/commands/`. After you
create the slash wrapper file, `/token-audit` should appear in the
available commands list on the next message. Ask the user to try
`/token-audit` (or `/token-audit 30` for a 30-day scan) to confirm.

### Step 6: Report back to the user

Tell the user:
- Files created (with paths)
- First audit result summary (avg start baseline %, sessions scanned)
- Top 3 recommendations from the tool
- How to run weekly: `/token-audit` (or `/token-audit 30`)

---

## FILE 1 — `token_audit.py` (the Python tool)

Save this verbatim. It is ~650 lines. It uses only the Python standard
library (no pip install needed). It requires Python 3.9 or newer.

```python
# ============================================================
# File: token_audit.py
# Purpose: Portable Claude Code token-consumption auditor.
#   - Measures workspace-side session-start baseline (CLAUDE.md,
#     memory files, command/skill inventory, hooks).
#   - Parses ~/.claude/projects/<hash>/*.jsonl transcripts to
#     extract real token usage (input, cache_creation, cache_read,
#     output) from each assistant turn.
#   - Aggregates avg start baseline, avg peak context, heaviest
#     sessions over a configurable scan window.
#   - Produces ranked recommendations with estimated savings.
# AI-Assisted: Yes. Originally drafted by Ea (vivi workspace),
#   2026-04-15, for portable use across any Claude Code setup.
# ============================================================

"""
Claude Code Token Audit — Portable Tool

Usage:
    python token_audit.py                 # JSON to stdout
    python token_audit.py --text          # human-readable summary
    python token_audit.py --markdown      # markdown report to stdout
    python token_audit.py --save          # save markdown report
    python token_audit.py --days 7        # scan last 7 days only
    python token_audit.py --top 10        # show top N heaviest sessions
    python token_audit.py --context-window 200000  # override window size

Exit codes:
    0 = success
    1 = no transcripts found for this workspace
    2 = unexpected error
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- Path setup ---
# Tries to use vivi's paths.py if present; otherwise falls back to
# a generic layout rooted at the current working directory.
PROJECT_ROOT = Path.cwd()
_script_dir = Path(__file__).resolve().parent

# Walk up from the script to find a paths.py (vivi convention)
for _up in range(5):
    _candidate = _script_dir.parents[_up] if _up < len(_script_dir.parents) else None
    if _candidate and (_candidate / "paths.py").exists():
        sys.path.insert(0, str(_candidate))
        PROJECT_ROOT = _candidate
        break

try:
    from paths import (
        PROJECT_ROOT as VIVI_ROOT,
        MEMORY_DIR,
        CORTEX_DIR,
        CORE_DIR,
    )
except ImportError:
    VIVI_ROOT = PROJECT_ROOT
    MEMORY_DIR = VIVI_ROOT / "system" / "memory"
    CORTEX_DIR = VIVI_ROOT / "system" / "cortex"
    CORE_DIR = VIVI_ROOT / "system" / "core"

CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"

# Where to save reports. Prefer vivi's health folder; fall back to
# .claude/reports/ for generic workspaces.
if MEMORY_DIR.exists():
    HEALTH_DIR = MEMORY_DIR / "health"
else:
    HEALTH_DIR = VIVI_ROOT / ".claude" / "reports"

# ~4 chars per token for mixed English/Bahasa text. Rough, but
# consistent enough for ratio comparisons.
CHARS_PER_TOKEN = 4.0

# Claude Code's displayed percentage uses an effective window of
# ~200K tokens regardless of the underlying model's larger window
# (e.g. Opus 4.6 1M). Override via --context-window if you prefer
# to measure against the actual window.
DEFAULT_CONTEXT_WINDOW = 200_000


# ------------------------------------------------------------
# Workspace measurement
# ------------------------------------------------------------

def file_size(path: Path) -> int:
    try:
        return path.stat().st_size if path.exists() else 0
    except OSError:
        return 0


def bytes_to_tokens(b: int) -> int:
    return int(b / CHARS_PER_TOKEN)


def measure_workspace_baseline() -> dict:
    """Measure the fixed cost of session start (workspace-side)."""
    claude_md = VIVI_ROOT / "CLAUDE.md"
    briefing = MEMORY_DIR / "_briefing.md"

    # vivi-specific memory vault sources; harmless on non-vivi
    # workspaces (they just won't exist and are skipped).
    memory_vault_files = [
        MEMORY_DIR / "profile" / "about.md",
        MEMORY_DIR / "profile" / "ai_persona.md",
        MEMORY_DIR / "work" / "daily_log.md",
        MEMORY_DIR / "projects" / "projects.md",
        MEMORY_DIR / "decisions" / "decisions.md",
        MEMORY_DIR / "learning" / "learnings.md",
        MEMORY_DIR / "work" / "todo.md",
        MEMORY_DIR / "work" / "tasks_view.md",
        MEMORY_DIR / "messaging" / "telegram_conversation.md",
        CORTEX_DIR / "data" / "patterns.md",
        CORE_DIR / "framework.md",
    ]
    memory_total = sum(file_size(p) for p in memory_vault_files)

    commands_dir = VIVI_ROOT / ".claude" / "commands"
    skills_dir = VIVI_ROOT / ".claude" / "skills"
    agents_dir = VIVI_ROOT / ".claude" / "agents"

    def count_md(d: Path) -> int:
        return len(list(d.glob("*.md"))) if d.exists() else 0

    settings_files = [
        VIVI_ROOT / ".claude" / "settings.local.json",
        VIVI_ROOT / ".claude" / "settings.json",
    ]
    hook_count = 0
    for settings in settings_files:
        if not settings.exists():
            continue
        try:
            cfg = json.loads(settings.read_text(encoding="utf-8"))
            hooks = cfg.get("hooks", {})
            for _, v in hooks.items():
                if isinstance(v, list):
                    hook_count += sum(len(h.get("hooks", [])) for h in v)
        except (OSError, json.JSONDecodeError):
            pass

    claude_md_bytes = file_size(claude_md)
    briefing_bytes = file_size(briefing)

    return {
        "claude_md": {
            "path": "CLAUDE.md" if claude_md.exists() else "MISSING",
            "bytes": claude_md_bytes,
            "tokens_est": bytes_to_tokens(claude_md_bytes),
        },
        "briefing": {
            "path": "system/memory/_briefing.md" if briefing.exists() else "MISSING",
            "bytes": briefing_bytes,
            "tokens_est": bytes_to_tokens(briefing_bytes),
            "exists": briefing.exists(),
        },
        "memory_vault_sources": {
            "total_bytes": memory_total,
            "tokens_est": bytes_to_tokens(memory_total),
            "files": [
                {"name": p.name, "bytes": file_size(p)}
                for p in memory_vault_files if file_size(p) > 0
            ],
        },
        "inventory": {
            "slash_commands": count_md(commands_dir),
            "skills": count_md(skills_dir),
            "agents": count_md(agents_dir),
        },
        "hooks_registered": hook_count,
    }


# ------------------------------------------------------------
# Claude Code transcript parsing
# ------------------------------------------------------------

def find_transcript_folder() -> Path | None:
    """Find the ~/.claude/projects/<hash>/ folder for this workspace.

    Primary strategy: derive the folder name by replacing `:`, `\\`,
    `/`, and `.` in the workspace path with `-` (Claude Code's
    normalization), then case-insensitive compare.

    Fallback: open each candidate folder's newest JSONL, scan lines
    until one has a `cwd` field, and match against this workspace.
    """
    if not CLAUDE_PROJECTS.exists():
        return None

    target = str(VIVI_ROOT).replace("\\", "/").rstrip("/").lower()

    candidates = [d for d in CLAUDE_PROJECTS.iterdir() if d.is_dir()]

    derived = str(VIVI_ROOT)
    for ch in (":", "\\", "/", "."):
        derived = derived.replace(ch, "-")
    for c in candidates:
        if c.name.lower() == derived.lower():
            return c

    for c in candidates:
        jsonls = sorted(c.glob("*.jsonl"),
                        key=lambda f: f.stat().st_mtime, reverse=True)
        for jsonl in jsonls[:3]:
            try:
                with open(jsonl, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i > 100:
                            break
                        try:
                            d = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        cwd = d.get("cwd", "")
                        if not cwd:
                            continue
                        if cwd.replace("\\", "/").lower().rstrip("/") == target:
                            return c
                        break
            except OSError:
                continue
    return None


def parse_transcript(jsonl: Path, context_window: int) -> dict | None:
    """Parse one JSONL transcript and extract usage stats."""
    session_id = jsonl.stem
    first_ts = None
    last_ts = None
    first_assistant_context = None
    peak_context = 0
    turn_count = 0
    total_output = 0
    total_cache_creation = 0
    total_cache_read = 0
    total_input = 0

    try:
        with open(jsonl, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = d.get("timestamp")
                if ts:
                    if first_ts is None:
                        first_ts = ts
                    last_ts = ts

                if d.get("type") != "assistant":
                    continue

                msg = d.get("message", {}) or {}
                usage = msg.get("usage") or {}
                if not usage:
                    continue

                turn_count += 1
                inp = usage.get("input_tokens", 0) or 0
                cc = usage.get("cache_creation_input_tokens", 0) or 0
                cr = usage.get("cache_read_input_tokens", 0) or 0
                out = usage.get("output_tokens", 0) or 0

                total_input += inp
                total_cache_creation += cc
                total_cache_read += cr
                total_output += out

                active_context = inp + cc + cr
                if first_assistant_context is None:
                    first_assistant_context = active_context
                if active_context > peak_context:
                    peak_context = active_context
    except OSError:
        return None

    if turn_count == 0:
        return None

    duration_s = 0
    if first_ts and last_ts:
        try:
            t1 = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
            duration_s = int((t2 - t1).total_seconds())
        except ValueError:
            pass

    return {
        "session_id": session_id,
        "started": first_ts,
        "ended": last_ts,
        "duration_seconds": duration_s,
        "turns": turn_count,
        "start_baseline_tokens": first_assistant_context or 0,
        "start_baseline_pct": round(
            100 * (first_assistant_context or 0) / context_window, 1
        ),
        "peak_context_tokens": peak_context,
        "peak_context_pct": round(100 * peak_context / context_window, 1),
        "total_output_tokens": total_output,
        "total_cache_creation": total_cache_creation,
        "total_cache_read": total_cache_read,
        "total_input": total_input,
        "file_bytes": file_size(jsonl),
    }


def scan_sessions(folder: Path, days: int, context_window: int) -> list:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_ts = cutoff.timestamp()
    sessions = []
    for jsonl in folder.glob("*.jsonl"):
        try:
            if jsonl.stat().st_mtime < cutoff_ts:
                continue
        except OSError:
            continue
        result = parse_transcript(jsonl, context_window)
        if result:
            sessions.append(result)
    sessions.sort(key=lambda s: s.get("started") or "", reverse=True)
    return sessions


def aggregate_sessions(sessions: list, context_window: int) -> dict:
    if not sessions:
        return {
            "session_count": 0,
            "avg_start_baseline_tokens": 0,
            "avg_start_baseline_pct": 0,
            "avg_peak_context_tokens": 0,
            "avg_peak_context_pct": 0,
            "total_output_tokens": 0,
            "total_cache_creation": 0,
            "total_cache_read": 0,
        }
    n = len(sessions)
    avg_start = sum(s["start_baseline_tokens"] for s in sessions) / n
    avg_peak = sum(s["peak_context_tokens"] for s in sessions) / n
    return {
        "session_count": n,
        "avg_start_baseline_tokens": int(avg_start),
        "avg_start_baseline_pct": round(100 * avg_start / context_window, 1),
        "avg_peak_context_tokens": int(avg_peak),
        "avg_peak_context_pct": round(100 * avg_peak / context_window, 1),
        "total_output_tokens": sum(s["total_output_tokens"] for s in sessions),
        "total_cache_creation": sum(s["total_cache_creation"] for s in sessions),
        "total_cache_read": sum(s["total_cache_read"] for s in sessions),
    }


# ------------------------------------------------------------
# Recommendations engine
# ------------------------------------------------------------

def build_recommendations(baseline: dict, agg: dict) -> list:
    recs = []

    claude_md_tokens = baseline["claude_md"]["tokens_est"]
    if claude_md_tokens > 6000:
        recs.append({
            "severity": "HIGH",
            "item": f"CLAUDE.md is large ({baseline['claude_md']['bytes']:,} bytes "
                    f"~ {claude_md_tokens:,} tokens)",
            "action": "Trim to 8-12 KB by moving section details (code standards, "
                      "compliance, cortex rules) to on-demand files with pointers.",
            "saving_tokens_est": claude_md_tokens - 2500,
        })

    briefing_tokens = baseline["briefing"]["tokens_est"]
    if baseline["briefing"]["exists"] and briefing_tokens > 4000:
        recs.append({
            "severity": "HIGH",
            "item": f"_briefing.md is large ({baseline['briefing']['bytes']:,} bytes "
                    f"~ {briefing_tokens:,} tokens)",
            "action": "Recompile briefing with a tighter budget (<4K tokens) or "
                      "switch to on-demand loading.",
            "saving_tokens_est": briefing_tokens - 1000,
        })

    if baseline["inventory"]["slash_commands"] > 30:
        recs.append({
            "severity": "MEDIUM",
            "item": f"{baseline['inventory']['slash_commands']} slash commands registered",
            "action": "Archive commands you have not used in the last 30 days.",
            "saving_tokens_est": 500,
        })

    if baseline["inventory"]["skills"] > 25:
        recs.append({
            "severity": "MEDIUM",
            "item": f"{baseline['inventory']['skills']} skills registered",
            "action": "Archive or remove unused skills from .claude/skills/.",
            "saving_tokens_est": 800,
        })

    avg_pct = agg.get("avg_start_baseline_pct", 0)
    if avg_pct > 12:
        recs.append({
            "severity": "HIGH",
            "item": f"Average session start baseline is {avg_pct}% - too high",
            "action": "Apply CLAUDE.md + briefing optimizations above. Target: <8%.",
            "saving_tokens_est": 0,
        })

    peak_pct = agg.get("avg_peak_context_pct", 0)
    if peak_pct > 60:
        recs.append({
            "severity": "MEDIUM",
            "item": f"Average peak context is {peak_pct}% - sessions grow large",
            "action": "Use /clear between unrelated tasks. Delegate heavy exploration "
                      "to sub-agents (Explore, general-purpose) so their context stays isolated.",
            "saving_tokens_est": 0,
        })

    if not recs:
        recs.append({
            "severity": "OK",
            "item": "No major issues detected",
            "action": "Baseline is healthy. Re-audit weekly to catch regressions.",
            "saving_tokens_est": 0,
        })

    return recs


# ------------------------------------------------------------
# Report rendering
# ------------------------------------------------------------

def render_text(report: dict, top_n: int) -> str:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    out = []
    out.append("=" * 60)
    out.append("  CLAUDE CODE - TOKEN AUDIT REPORT")
    out.append("=" * 60)
    out.append(f"Workspace:  {report['workspace']}")
    out.append(f"Date:       {report['date']}")
    out.append(f"Context win: {report['context_window']:,} tokens (assumed)")
    out.append(f"Scan range: last {report['scan_days']} days")
    out.append("")

    b = report["baseline"]
    out.append("-- Session Start Baseline (workspace-side files) --")
    out.append(f"  CLAUDE.md          {b['claude_md']['bytes']:>8,} B  "
               f"~ {b['claude_md']['tokens_est']:>6,} tokens")
    br = b["briefing"]
    if br["exists"]:
        out.append(f"  _briefing.md       {br['bytes']:>8,} B  "
                   f"~ {br['tokens_est']:>6,} tokens  (on demand)")
    else:
        out.append("  _briefing.md       (not present)")
    mv = b["memory_vault_sources"]
    if mv["total_bytes"] > 0:
        out.append(f"  Memory vault src   {mv['total_bytes']:>8,} B  "
                   f"~ {mv['tokens_est']:>6,} tokens")
    inv = b["inventory"]
    out.append(f"  Inventory          commands={inv['slash_commands']}  "
               f"skills={inv['skills']}  agents={inv['agents']}")
    out.append(f"  Hooks registered   {b['hooks_registered']}")
    out.append("")

    agg = report["sessions_aggregate"]
    out.append("-- Real Usage (parsed from transcripts) --")
    out.append(f"  Sessions scanned        {agg['session_count']}")
    if agg["session_count"] > 0:
        out.append(f"  Avg start baseline      {agg['avg_start_baseline_tokens']:>7,} "
                   f"tokens ({agg['avg_start_baseline_pct']}%)")
        out.append(f"  Avg peak context        {agg['avg_peak_context_tokens']:>7,} "
                   f"tokens ({agg['avg_peak_context_pct']}%)")
        out.append(f"  Total output tokens     {agg['total_output_tokens']:>12,}")
        out.append(f"  Total cache_creation    {agg['total_cache_creation']:>12,}")
        out.append(f"  Total cache_read        {agg['total_cache_read']:>12,}")
    out.append("")

    sessions = report["sessions"]
    if sessions:
        out.append(f"-- Top {min(top_n, len(sessions))} Heaviest Sessions (by peak context) --")
        sorted_s = sorted(sessions, key=lambda s: s["peak_context_tokens"], reverse=True)[:top_n]
        for i, s in enumerate(sorted_s, 1):
            started = (s["started"] or "")[:16].replace("T", " ")
            out.append(f"  {i:2}. {started}  "
                       f"peak={s['peak_context_pct']:>5}%  "
                       f"turns={s['turns']:>3}  "
                       f"out={s['total_output_tokens']:>6,}  "
                       f"id={s['session_id'][:8]}")
        out.append("")

    out.append("-- Recommendations --")
    for i, r in enumerate(report["recommendations"], 1):
        tag = f"[{r['severity']}]"
        out.append(f"  {i}. {tag:<10} {r['item']}")
        out.append(f"       -> {r['action']}")
        if r.get("saving_tokens_est"):
            out.append(f"       ~saving: {r['saving_tokens_est']:,} tokens/session")
    out.append("")
    out.append("=" * 60)
    return "\n".join(out)


def render_markdown(report: dict, top_n: int) -> str:
    lines = []
    lines.append(f"# Token Audit Report - {report['date']}")
    lines.append("")
    lines.append(f"**Workspace:** `{report['workspace']}`  ")
    lines.append(f"**Context window:** {report['context_window']:,} tokens  ")
    lines.append(f"**Scan range:** last {report['scan_days']} days")
    lines.append("")

    lines.append("## Session Start Baseline")
    lines.append("")
    b = report["baseline"]
    lines.append("| Component | Bytes | Est. Tokens |")
    lines.append("|---|---:|---:|")
    lines.append(f"| CLAUDE.md | {b['claude_md']['bytes']:,} | {b['claude_md']['tokens_est']:,} |")
    if b["briefing"]["exists"]:
        lines.append(f"| _briefing.md | {b['briefing']['bytes']:,} | {b['briefing']['tokens_est']:,} |")
    if b["memory_vault_sources"]["total_bytes"] > 0:
        lines.append(f"| Memory vault sources | {b['memory_vault_sources']['total_bytes']:,} | {b['memory_vault_sources']['tokens_est']:,} |")
    lines.append("")
    inv = b["inventory"]
    lines.append(f"**Inventory:** {inv['slash_commands']} slash commands, "
                 f"{inv['skills']} skills, {inv['agents']} agents, "
                 f"{b['hooks_registered']} hooks")
    lines.append("")

    agg = report["sessions_aggregate"]
    lines.append("## Real Usage (Parsed Transcripts)")
    lines.append("")
    lines.append(f"- Sessions scanned: **{agg['session_count']}**")
    if agg["session_count"] > 0:
        lines.append(f"- Avg start baseline: **{agg['avg_start_baseline_tokens']:,} tokens "
                     f"({agg['avg_start_baseline_pct']}%)**")
        lines.append(f"- Avg peak context: **{agg['avg_peak_context_tokens']:,} tokens "
                     f"({agg['avg_peak_context_pct']}%)**")
        lines.append(f"- Total output tokens: {agg['total_output_tokens']:,}")
        lines.append(f"- Total cache creation: {agg['total_cache_creation']:,}")
        lines.append(f"- Total cache read: {agg['total_cache_read']:,}")
    lines.append("")

    sessions = report["sessions"]
    if sessions:
        lines.append(f"## Top {min(top_n, len(sessions))} Heaviest Sessions")
        lines.append("")
        lines.append("| # | Started | Peak | Turns | Output | Session ID |")
        lines.append("|---:|---|---:|---:|---:|---|")
        sorted_s = sorted(sessions, key=lambda s: s["peak_context_tokens"], reverse=True)[:top_n]
        for i, s in enumerate(sorted_s, 1):
            started = (s["started"] or "")[:16].replace("T", " ")
            lines.append(f"| {i} | {started} | {s['peak_context_pct']}% | "
                         f"{s['turns']} | {s['total_output_tokens']:,} | "
                         f"`{s['session_id'][:8]}` |")
        lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    for i, r in enumerate(report["recommendations"], 1):
        lines.append(f"### {i}. [{r['severity']}] {r['item']}")
        lines.append("")
        lines.append(f"**Action:** {r['action']}")
        if r.get("saving_tokens_est"):
            lines.append("")
            lines.append(f"**Estimated saving:** ~{r['saving_tokens_est']:,} tokens per session")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by token_audit.py on {report['date']}*")
    return "\n".join(lines)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Audit Claude Code token consumption for this workspace."
    )
    parser.add_argument("--text", action="store_true",
                        help="Print human-readable text summary (default: JSON)")
    parser.add_argument("--markdown", action="store_true",
                        help="Print markdown report to stdout")
    parser.add_argument("--save", action="store_true",
                        help="Save markdown report to the health/reports folder")
    parser.add_argument("--days", type=int, default=30,
                        help="Scan transcripts from the last N days (default: 30)")
    parser.add_argument("--top", type=int, default=10,
                        help="Show top N heaviest sessions (default: 10)")
    parser.add_argument("--context-window", type=int, default=DEFAULT_CONTEXT_WINDOW,
                        help=f"Assumed context window size (default: {DEFAULT_CONTEXT_WINDOW:,})")
    args = parser.parse_args()

    baseline = measure_workspace_baseline()

    folder = find_transcript_folder()
    sessions = []
    if folder is None:
        note = ("No Claude Code transcript folder found for this workspace. "
                "Have you used Claude Code here yet?")
    else:
        sessions = scan_sessions(folder, args.days, args.context_window)
        note = f"Parsed {len(sessions)} sessions from {folder}"

    agg = aggregate_sessions(sessions, args.context_window)
    recs = build_recommendations(baseline, agg)

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(VIVI_ROOT),
        "context_window": args.context_window,
        "scan_days": args.days,
        "transcript_folder": str(folder) if folder else None,
        "note": note,
        "baseline": baseline,
        "sessions_aggregate": agg,
        "sessions": sessions,
        "recommendations": recs,
    }

    if args.save:
        HEALTH_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        out_path = HEALTH_DIR / f"{stamp}_token_audit.md"
        out_path.write_text(render_markdown(report, args.top), encoding="utf-8")
        print(f"Saved: {out_path}")

    if args.markdown:
        print(render_markdown(report, args.top))
    elif args.text:
        print(render_text(report, args.top))
    else:
        print(json.dumps(report, indent=2, default=str))

    if folder is None:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
```

---

## FILE 2 — Command workflow (vivi workspaces only)

Save as `system/cortex/commands/token-audit.md` for vivi workspaces.
**Skip this file for generic workspaces** — use FILE 3 instead.

```markdown
---
command: TOKEN-AUDIT
description: Audit Claude Code token consumption — baseline cost, real usage from transcripts, optimization recommendations
arguments:
  - name: days
    required: false
    description: "Scan transcripts from the last N days (default: 14)"
  - name: top
    required: false
    description: "Show top N heaviest sessions (default: 10)"
aliases:
  - TOKEN-AUDIT
  - AUDIT-TOKEN
  - CLAUDE-AUDIT
  - CONTEXT-AUDIT
triggers:
  - "audit token"
  - "audit claude code"
  - "why is claude code using so many tokens"
  - "kenapa token cepat habis"
  - "analisa pemakaian token"
version: 1
---

# TOKEN-AUDIT

## Description

Measure and explain Claude Code token consumption for this workspace.
Produces a structured report: session-start baseline, real usage
from JSONL transcripts, aggregates, and ranked recommendations.

## Pre-Conditions

- `python` 3.9+ on PATH
- `system/cortex/tools/token_audit.py` exists
- User has used Claude Code in this workspace at least once

## Workflow

### Step 1: Run the audit

```bash
python system/cortex/tools/token_audit.py --text --save --days 14 --top 10
```

If the user passed arguments (e.g. `TOKEN-AUDIT 30`), use those
instead of the defaults.

### Step 2: Check for prior audit

```bash
ls -t system/memory/health/*token_audit.md 2>/dev/null | head -2
```

If a prior report exists, compare avg start baseline and avg peak
context. Note whether trend is better, worse, or flat.

### Step 3: Present findings in chat

Structure: baseline %, top 3 contributors, top 3 recommendations,
trend vs. last audit, saved report path. Keep under 250 words.

### Step 4: Offer next action

- If HIGH recommendations exist and no fix is applied yet: offer to
  apply the top quick-win.
- If baseline is healthy (<8%): suggest re-audit next week.
- If trend worsens: offer to investigate the cause.

## Rollback

Read-only command — nothing to roll back. Delete files in
`system/memory/health/` if you want to clear audit history.

## Examples

- `TOKEN-AUDIT` → last 14 days, top 10
- `TOKEN-AUDIT 30` → last 30 days
- `TOKEN-AUDIT 7 5` → last 7 days, top 5
```

---

## FILE 3 — Slash wrapper

For **vivi workspaces**, save as `.claude/commands/token-audit.md`:

```markdown
Audit Claude Code token consumption for this workspace — session-start baseline, real transcript usage, optimization recommendations. Read and execute the workflow defined in `system/cortex/commands/token-audit.md`. Follow every step sequentially. User arguments: $ARGUMENTS
```

For **generic workspaces** (no separate workflow file), save as
`.claude/commands/token-audit.md` with the workflow inlined:

```markdown
Run a Claude Code token consumption audit for this workspace.

User arguments: $ARGUMENTS (optional: `days` `top`, e.g. `/token-audit 30 10`)

Workflow:

1. Execute the audit tool:
   ```
   python .claude/tools/token_audit.py --text --save --days 14 --top 10
   ```
   If the user passed arguments, substitute them for the defaults.

2. Capture the saved report path from the tool's first line of output.

3. Check for a prior audit report in `.claude/reports/` — if one
   exists, compare avg start baseline and avg peak context to detect
   trend direction (improving, worsening, flat).

4. Present findings in chat — under 250 words. Include:
   - Avg start baseline % and avg peak context %
   - Top 3 biggest contributors (CLAUDE.md size, briefing size, etc.)
   - Top 3 recommendations with estimated savings
   - Trend vs. last audit (if prior report existed)
   - Path to the saved markdown report

5. Offer one concrete next action:
   - HIGH recommendations exist → offer to apply the top quick-win
   - Baseline healthy (<8%) → suggest re-audit next week
   - Trend worsening → offer to investigate

Do not paste the full report into chat — it is already saved to disk.
```

---

## Verification Checklist

After installation, run through this checklist:

- [ ] `python <tool path> --text --days 14` prints a report (no errors)
- [ ] "Session Start Baseline" section shows a non-zero `CLAUDE.md` size
      (or "MISSING" if the workspace has no CLAUDE.md)
- [ ] "Real Usage" section shows `Sessions scanned: N` with N > 0
      (assuming the user has used Claude Code here before)
- [ ] `/token-audit` is listed among available slash commands in the
      next Claude Code message
- [ ] `/token-audit` in chat triggers the workflow and produces a
      chat summary plus a saved markdown report

---

## Troubleshooting

**"Sessions scanned: 0"**

- The auto-match for `~/.claude/projects/<hash>/` failed. Check:
  ```bash
  ls ~/.claude/projects/
  ```
- Derive the expected folder name from your workspace path: replace
  `:`, `\`, `/`, and `.` with `-`. Example: `C:\Users\john\proj` →
  `C--Users-john-proj`.
- If the folder exists but is not matched, pass it manually — open
  the tool and add a hardcoded fallback in `find_transcript_folder()`.

**"No Claude Code transcript folder found"**

- You have never used Claude Code in this workspace. Use it for a
  session or two, then re-run the audit.

**"UnicodeEncodeError" on Windows (cp1252 codec)**

- The tool already calls `sys.stdout.reconfigure(encoding="utf-8")`
  in `render_text`. If you still see this on an old Python, run:
  ```bash
  set PYTHONIOENCODING=utf-8
  python <tool path> --text
  ```

**Peak context percentages over 100%**

- Claude Code's displayed percentage uses a 200K effective window
  by default, but Opus 4.6 supports 1M. Pass `--context-window 1000000`
  for an accurate percentage. Absolute token counts are always correct.

**"ModuleNotFoundError: No module named 'paths'"**

- Harmless — the tool tries to import vivi's `paths.py` and falls
  back gracefully. If you see this as a hard error, check that the
  `try/except ImportError` block in the Python file was copied
  correctly.

---

## License / Attribution

This recipe was produced with AI assistance (Claude Opus 4.6 via
Claude Code) on 2026-04-15. Free to copy, modify, and redistribute
within the Lam Seng Hang group and partner organizations. No
warranty. Use at your own discretion.

**Reviewed by:** Yoza Wiratama (IT Department, Lam Seng Hang)
**Original workspace:** Ea (vivi — Virtual Virtuoso)
