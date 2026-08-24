# ReRAM-SMU V1 — MCP Setup

**Date:** 2026-08-24  
**Hermes MCP state:** `hermes mcp list` → 0 configured (`hermes mcp catalog` shows 20 available: airtable, asana, atlassian, ... vercel, webflow — none KiCad/SPICE-specific)

## 1. Evaluation

### Hermes catalog (20 servers)
All are productivity/cloud-oriented (Airtable/Notion/Figma/Linear/Netlify/Vercel/Sentry/Stripe/Supabase/Unreal). No KiCad, SPICE, or scientific-Python server in catalog. Not relevant to Phase 0 exit criteria.

### GitHub search `kicad mcp server` (top result)
| Field | Value |
|-------|-------|
| Repo | `mixelpixx/KiCAD-MCP-Server` |
| Stats | 1947★, 302 forks, Python, started 2025-04-26, updated 2026-08-24, pushed 2026-08-20, 20 open issues |
| License | MIT (`https://api.github.com/licenses/mit`) — **PASS** (usable license) |
| Homepage | none |
| Description | MCP that lets LLMs directly interact with KiCad for PCB design |

**Quick source scan (without cloning full tree — via API metadata + prior review):**

- Language Python, has wiki, discussions, issues — active maintenance (pushed 4 days ago).
- README advertises direct file manipulation of `*.kicad_sch`/`*.kicad_pcb`, subprocess calls to `kicad-cli`, and filesystem watchers.
- No Hermes-native catalog entry — would be added via `hermes mcp add --command python --args ...` with a filesystem root Arg.

**Other candidates considered (lower priority):**
- No other KiCad MCP with >100 stars that is narrowly scoped; alternatives are forks of the above or abandoned (<50 stars, last push >12 months).

## 2. Decision (DEC-TOOL-005)

**No MCP installed in Phase 0.** KiCad MCP is **CANDIDATE / DEFERRED** for Phase 2.

**Rationale:**
- Phase 0 has no schematic/PCB to automate — MCP would add privilege without value (violates minimal-privilege).
- Filesystem scope would need to be `E:\ReRAM-SMU V1` narrowly — current server defaults to broader project or home. Narrowing requires config audit per-repo and a test harness (not justified in Phase 0).
- `computer_use` + `kicad-cli` already provide safe automation paths for Phase 0 (background GUI via `computer_use`, headless via `kicad-cli`).

## 3. Security implications (summary — details in SECURITY_REVIEW.md)

- Filesystem access: would need to be constrained to `E:\ReRAM-SMU V1` (not `C:`, `E:`, or user profile).
- Subprocess: spawns `kicad-cli`, potentially `python`/`pcbnew` — requires allowlisted commands.
- Network: none by default (stdio MCP) — low exfiltration risk if not misconfigured.
- Risk if installed now: accidental schematic corruption, overly broad file access, destructive PCB edits without safeguards.

## 4. If installed in future (Phase 2 gating)

```powershell
# Example future install — NOT executed now
hermes mcp add kicad --command "C:\Users\azrai\AppData\Local\Programs\Python\...\python.exe" --args "E:\ReRAM-SMU V1\tools\mcp\kicad-mcp\server.py"
# Then in mcp_servers config, set filesystem root:
#   "filesystem_root": "E:\\ReRAM-SMU V1"
# and allowlist commands: ["E:\\KiCad\\bin\\kicad-cli.exe"]
```

Before that, re-audit after cloning the repo at `tools/mcp/kicad-mcp/` and reviewing `README`, `pyproject.toml`/`requirements.txt`, `server.py`, and filesystem/subprocess code per SECURITY_REVIEW.md checklist.

## 5. Verification

```powershell
hermes mcp list    # → 0 servers (intentional)
hermes mcp catalog # → 20 available, none installed
```

Residual risk: **NONE** in Phase 0 (no MCP with file/network access installed).
