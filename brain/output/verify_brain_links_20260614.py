#!/usr/bin/env python3
"""Resolve every relative + brain-relative link in brain/*.md and report broken ones,
classified so we can confirm the relocation introduced no new breakage."""
import os, re

BRAIN = "/Users/christopherfryman/Documents/code/AOP MAP/brain"
MOVED = ["02_edit","04_edit","05_special_operation","07_tables",
         "08_data_normalization","11_client_convergence",
         "12_field_schedule_editor","13_viewer_extraction"]
PATH_RE = re.compile(r'((?:\.\./|\./)[A-Za-z0-9_./\-]+|tasks/[A-Za-z0-9_./\-]+)')

def is_historical(rel):
    return (rel.startswith("output/") or rel.startswith("handoff/coord/")
            or re.match(r"handoff/session_context_\d", rel))

def points_to_moved(target_rel):
    for s in MOVED:
        if target_rel == f"tasks/{s}" or target_rel.startswith(f"tasks/{s}/"):
            return True
    return False

broken = []  # (file, token, kind)
for root, _, files in os.walk(BRAIN):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        rel = os.path.relpath(os.path.join(root, fn), BRAIN)
        with open(os.path.join(root, fn), encoding="utf-8") as fh:
            text = fh.read()
        cur_dir = os.path.dirname(rel)
        for tok in set(PATH_RE.findall(text)):
            if tok.startswith("tasks/"):
                target = tok  # brain-relative
            else:
                target = os.path.normpath(os.path.join(cur_dir, tok))
            # ignore links that escape brain (repo-relative descriptive paths)
            if target.startswith(".."):
                continue
            if not os.path.exists(os.path.join(BRAIN, target.rstrip("/"))):
                # is the resolved/intended target a moved sprint (stale-to-old-path)?
                stale_to_moved = points_to_moved(target)
                broken.append((rel, tok, "hist" if is_historical(rel) else "active",
                               "->MOVED" if stale_to_moved else "other"))

# report
active_moved = [b for b in broken if b[2]=="active" and b[3]=="->MOVED"]
active_other = [b for b in broken if b[2]=="active" and b[3]=="other"]
hist_moved   = [b for b in broken if b[2]=="hist"   and b[3]=="->MOVED"]
hist_other   = [b for b in broken if b[2]=="hist"   and b[3]=="other"]

print(f"BROKEN LINK SUMMARY (resolving brain-internal links only)")
print(f"  ACTIVE files, point to a MOVED sprint (== my omissions, MUST be 0): {len(active_moved)}")
for f,t,_,_ in active_moved: print(f"      {f}  ::  {t}")
print(f"  ACTIVE files, other broken (pre-existing debt, not my move): {len(active_other)}")
for f,t,_,_ in sorted(active_other): print(f"      {f}  ::  {t}")
print(f"  HISTORICAL files -> MOVED sprint (intentionally left stale): {len(hist_moved)}")
print(f"  HISTORICAL files, other broken (pre-existing): {len(hist_other)}")
