# Water, gathering 04

This round checks four public-evidence worker tools, shares domain binding with
the payment bridge, rebuilds the cave gallery, and leaves **The Bound Eye**.
No line folder, wallet, key, signing flow or external submission is changed.

One offline command verifies the four lines and shared pieces:

```sh
python3 -B gathering/run_checks.py
```

It runs each documented check and offline demonstration, including the four
mark-24 additions. Tests which write beside an ancestor source run on an exact
copy in `test/scratch/`. All bytecode generation is disabled. The final run
passed 221 tests and all 32 commands; `check-results.json` retains the results.
Checks are local observations, not independent certification.

The useful new shared command is documented in
`../shared/payment-evidence/README.md`: `bind.py` requires a replayed ZTO/IMD
payment, exact client commitment and separately supplied domain/type to agree.
The detached copy trial is recorded in `portable-check-04.json`. Fresh public
Ethereum trials are in `live-check-results-04.json`, `anchored-round04.json`
and the bridge's `round04.*.json`. Those transcripts retain historical provider
observations; the demo policy was derived from the receipt, not an invoice.
`live_checks.py` uses the public endpoint normally; this runtime routed its reads
through the assignment's supplied transport without persisting its address.

`REPORT.md` replaces the previous report and lists per-line trials, working
behavior, unresolved limits, shared changes and scope. `COINS.md` says none:
ZTO already supplies practical payment evidence and IMD is supported second.

The whole gathering wall is **1254 × 1254 RGB PNG** at
`artifacts/gathering/wall.png` and required `artifacts/gathering/wall-v4.png`.
The preview is **512 × 512 JPEG**, 75,232 bytes, at `dist/gathering/04.jpg`;
its record `04.json` uses the PNG's lowercase SHA-256 artifact URL. The installed
image generator made one ochre-loop/charcoal-eye pigment draft. A one-time local
composition added only that pigment to vacant stone; all outside pixels and deep
cracks remain unchanged. `finish_wall_04.py` documents this process and refuses
to run unless `wall.png` is the verified gathering-03 ancestor. It is a finishing
record, not a command to regenerate the current deliverable.

Both the full PNG and decoded JPEG were inspected: ancestor Pepe, rock, light,
cracks, water and framing remain intact. No hands/handprints are depicted, so no
digits are present. No text, forbidden marks, borders or frames observed.
**No known unmet visual requirements.** Counts, format and inspection notes are
in `wall-review-04.json`.

`dist/index.html` is one dependency-free page with inline styles and captions;
all 117 inherited/current records appear by wall, newest painted mark first,
with future slots expandable. Painted JPEGs load locally offline; full-size walls
and unpainted cave images use public artifact URLs. Four goals are copied exactly
from their unchanged GOAL.md files to `dist/goals.json`. This is the fourth
painted gathering, so the first-gathering placeholder creation rule does not
apply; existing future records remain untouched.

Rebuild the page and check delivery:

```sh
python3 -B gathering/build_gallery.py
python3 -B gathering/check_delivery.py
```

The latter validates image structure, record/hash/traits, previews, placeholder
coverage, gallery order, goals, vendored provenance, unchanged line-folder hashes
and the 100 KB file cap outside artifacts. It requires the locally delivered wall
files. Named PNG outputs remain untracked for the daemon to upload separately.
