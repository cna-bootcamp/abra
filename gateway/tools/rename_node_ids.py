"""Auto-detect and rename hyphenated Dify node IDs to underscored versions.

Dify's VariableTemplateParser regex `[a-zA-Z0-9_]{1,50}` does NOT allow hyphens.
All node IDs must use underscores so `{{#node_id.field#}}` templates resolve at runtime.

What this script does:
- Parses the target DSL YAML
- Enumerates every `workflow.graph.nodes[].id` containing a hyphen
- Builds a rename map (`old -> old.replace('-', '_')`) automatically
- Applies the rename as a safe token-boundary substitution across the whole file:
  node.id, edges[].source/target, every value_selector[0], every {{#id.x#}} template ref

What this script preserves (skipped by design):
- question-classifier `classes[].id` (e.g., `class-gather`) — runtime handle IDs, not node IDs
- edges[].id (e.g., `edge-*`) — edge identifiers, not node IDs
- conversation_variables[].id — UUIDs; must stay as-is (and must be UUID v4)
- `[conversation, X]`, `[sys, X]`, `[env, X]` selectors — reserved scopes

Usage:
    python rename_node_ids.py <dsl_path>
    python rename_node_ids.py <dsl_path> --dry-run    # preview without writing
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Activate gateway venv first.", file=sys.stderr)
    sys.exit(2)


def collect_hyphenated_node_ids(dsl: dict) -> list[str]:
    """Return the sorted list of workflow.graph.nodes[].id values that contain a hyphen."""
    workflow = dsl.get("workflow") or {}
    graph = workflow.get("graph") or {}
    nodes = graph.get("nodes") or []
    hyphenated: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        nid = node.get("id")
        if isinstance(nid, str) and "-" in nid:
            hyphenated.add(nid)
    return sorted(hyphenated)


def build_rename_map(ids: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for old in ids:
        new = old.replace("-", "_")
        if new != old:
            mapping[old] = new
    return mapping


def apply_rename(text: str, mapping: dict[str, str]) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    # Replace longest keys first to avoid partial collisions.
    for old in sorted(mapping.keys(), key=len, reverse=True):
        new = mapping[old]
        # Word boundary: neither neighbor may be a continuing identifier char.
        pattern = re.compile(r"(?<![a-zA-Z0-9_-])" + re.escape(old) + r"(?![a-zA-Z0-9_-])")
        text, count = pattern.subn(new, text)
        counts[old] = count
    return text, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dsl_path", help="Path to the DSL YAML file")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    src = Path(args.dsl_path)
    if not src.exists():
        print(f"[ERROR] File not found: {src}", file=sys.stderr)
        return 2

    raw = src.read_text(encoding="utf-8")
    try:
        dsl = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        print(f"[ERROR] YAML parse failed: {e}", file=sys.stderr)
        return 2

    ids = collect_hyphenated_node_ids(dsl)
    if not ids:
        print("[OK] No hyphenated node IDs detected. Nothing to rename.")
        return 0

    mapping = build_rename_map(ids)
    print(f"[INFO] Detected {len(mapping)} hyphenated node ID(s):")
    for old, new in mapping.items():
        print(f"  {old}  ->  {new}")

    new_text, counts = apply_rename(raw, mapping)
    total = sum(counts.values())

    print()
    print("[INFO] Replacements per identifier:")
    for old, count in counts.items():
        print(f"  {old}: {count}")
    print(f"[INFO] Total replacements: {total}")

    if args.dry_run:
        print("[DRY-RUN] File not modified.")
        return 0

    src.write_text(new_text, encoding="utf-8")
    print(f"[OK] File updated: {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
