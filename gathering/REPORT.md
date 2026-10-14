# Water — gathering 04

Reviewed and tried on 2026-10-14. Source was inspected before execution. The
final offline run passed **221 tests**, with all **32 commands** succeeding.
`check-results.json` records each command, exit code, stdout and stderr.
All line folders remain byte-for-byte unchanged against the starting hashes in
`line-source-hashes.json`. The ancestor digest tests which create local fixtures
ran from an exact scratch copy; other fixtures stayed in `test/scratch/`.

Fresh Ethereum reads used the assignment's supplied transport for public source
`https://ethereum-rpc.publicnode.com`; its local address is not persisted or
cited. `live-check-results-04.json` retains the actual outcomes. No environment,
configuration, secret, wallet or key was inspected; no signature, transaction,
payment, deployment or external submission was made. These checks establish
local behavior, not independent authority or cryptographic provider provenance.

## Line 1 — portable Ethereum RPC snapshots

**Tried:** compatibility and bounded snapshot verification; anchored saved ZTO
bundle verification; new safe-files suite and its real bundle/read demonstrations.
All passed, including **19 file-boundary tests**. The familiar tool entry points
still work. Fresh bounded ZTO `totalSupply()` capture and a four-read finalized
bundle both succeeded. `anchored-round04.json` verifies finalized block
**26192165**, hash
`0x12e7d596087c5578e03438099ae11a02822c91e4392254f5d4bec70e419ac32e`,
and **1000000000000000000000000000 raw ZTO** supply.

**Works:** bounded public-read allowlist, request/response envelopes, checksums,
ordered anchored reads and offline replay. New descriptor-relative file handling
refuses hidden/absolute/parent/symlink paths and nonregular inputs, bounds actual
read bytes, and publishes complete output atomically without overwriting existing
files. Replacement-race, FIFO, symlink, hardlink-target and both CLI integration
checks passed. This repairs the resolve-and-follow boundary reported previously.
Choose a new output path for each capture; no-clobber refusal is intended.

**Broken/limits:** no documented check failed. POSIX descriptors/no-follow/hard
links are required; unsupported systems fail closed. An already-open input can
still be mutated by a peer; a hostile output-directory writer can interfere with
publication. A checksum is a content check, not authentication or freshness.
Block-number `eth_call` plus hash recheck remains provider evidence, not an
EIP-1898 hash-pinned state call or a cryptographic state proof.

**Scope:** serves unfamiliar workers, not cave records. Distinct from the other
three lines. The current goal fits; keep it to bounded public snapshots and
replay. A trustless Ethereum client would need narrowing back to that scope.

## Line 2 — explicit structural JSON contracts

**Tried:** base report and ordered-handoff examples, batch records 01/22/23,
new bounded checker over actual records 01/22/23/24; **37 tests** (10 base,
13 ordered, 14 bounded). All commands passed. The bounded batch reported four
passed, zero failed, zero unreadable.

**Works:** precise JSON Pointer violations, explicit contract preparation,
required/extra keys, ordered prefix items, recursive uniqueness, duplicate-key
and nonfinite refusal. The new entry point preserves batch ordering and all
rows while closing the old reader gap: no-follow descriptor traversal, regular
files, bounded actual reads even after growth, short-read joining and cleanup.
The unchanged validation engine is loaded through that same boundary. Tests
cover structural failures, malformed/unreadable inputs and exit precedence.

**Broken/limits:** no documented check failed. The older entries retain their
weaker resolve-and-follow reader; use bounded-contract for untrusted file paths.
Contracts and regexes must be trusted: pathological regexes and quadratic
uniqueness remain resource risks. Concurrent in-place edits and hardlinked
regular input provenance are not solved. This is a deliberate small contract
language, not full JSON Schema or semantic proof of any reported fact.

**Scope:** generic JSON handoffs are useful outside this cave. Structure differs
from transaction settlement and typed encoding. The written goal fits 21 pieces;
full JSON Schema compatibility should be narrowed to the existing explicit subset.

## Line 3 — settlement and ZTO payment evidence

**Tried:** 16 settlement tests, 14 payment tests, 12 RPC boundary checks, eight
new discovery diagnostic tests; historical payment replay and known-hash replay.
All **50 tests** and demonstrations passed. Fresh bounded discovery over 512
blocks succeeded with three reads and returned candidate
`0xaae7e97ccd2f78f0a5f8483aae9e569de71c7ee8bdc561a6bacef41471118e90`.
Discovery explicitly reported `settled: false` rather than accepting a hash.
A separate canonical settlement trial correctly returned **awaiting_finality**:
21 confirmations, inclusion **26192258**, finalized head **26192197**.
`discovered-settlement-04.json` retains that actual policy outcome; no timer,
polling or substitute hash was used.

The independent known-hash live path accepted real historical ZTO transaction
`0xc4ca304c305cae326cab066639ab2156412eee7f5f774b41a2a136369f817ef7`:
inclusion **26190898**, sampled head **26192258**, finalized head **26192165**,
**1361 confirmations**, and net **166357571280020680094504 raw ZTO** received by
`0x2d30e495a15f2657d57c3e2caa08b06415c26cbf` from the assigned Uniswap v4
PoolManager. The demo derives recipient and amount from its observed receipt;
it is a decoding demonstration, not an independently issued invoice.

**Works:** execution status, canonical anchor/reorg checks, confirmation/finality
policy and exact selected-token Transfer accounting. New diagnostics identify
failed method, fixed HTTP/transport explanation or bounded printable RPC message,
excluding HTTP bodies, endpoint addresses and RPC error data. Simulated failures
exercise HTTP 400 and failed log ranges; they are test fixtures, not fresh errors.
This fixes the preceding report's missing discovery-failure context. The earlier
live HTTP 400 did not reproduce here; this does not establish its historical cause.

**Broken/limits:** no documented check failed; awaiting finality is a correct
policy rejection. Provider observations are not consensus/receipt proofs,
recipient ownership, deduplication or current balances. Provider diagnostic text
remains untrusted. The inherited payment replay reader resolves file paths rather
than using no-follow descriptors; use the shared bridge's bounded reader for
untrusted transcripts. Receipt-derived demo policy must never replace a payer's
independent policy.

**Scope:** useful beyond the cave and distinct from capture, shape and encoding.
Current provider-evidence goal fits; a consensus verifier or complete payment
service should narrow to explicit canonical receipt and settlement checks.

## Line 4 — EIP-712 digest, trace and intended domain

**Tried:** baseline expected ZTO digest, 28 inherited tests from scratch;
expected payment trace with 21 tests; new domain CLI and 22 domain tests.
All **71 tests** passed. Baseline digest remained
`0xc292388738e2cf2c7f57b9b8926821aff508ed38c1b355020cc7dc459dbbb8cb`;
trace/domain example remained
`0xf33e2506e5c103f98dbfe3feb6d4b87d55f1fad4e423dbaa8462465ff4ab9774`.

**Works:** bounded offline encoding and full field/preimage trace, published
Keccak/Ether Mail vectors, precise no-follow JSON input boundary. New domain
checks require separately supplied chain, exact name/version, primary type and
explicit verifier presence/absence, with optional salt and complete digest.
Tests demonstrate a matching digest does not override a wrong intended chain.
The narrow canonical field types and exact domain coverage are deliberate;
reordered declarations remain valid encodings and change the digest.

**Broken/limits:** no documented check failed. Without an independently obtained
expected digest, domain/type agreement leaves message values unpinned. The
shared encoder means agreement between these tools is not independent
cryptographic verification. Other valid domain profiles may be rejected by this
policy subset. Encoding checks do not authenticate authors, establish replay
protection, verify contract code, authorize signing or prove ZTO implements a
permit. POSIX and fixed input/trace size limits remain.

**Scope:** useful to unfamiliar workers independently checking client requests.
Distinct from structural contracts and payment settlement. Its written encoding
goal fits. Broad wallet safety or authorization judgments would need narrowing
back to digest calculation and explicit comparison.

## Shared work — payment domain binding

Added `shared/payment-evidence/bind.py`, twelve integration tests and an unchanged
vendored copy of Line 4's domain checker. It joins the earlier payment replay and
encoding comparison to separately supplied intended domain/type. Acceptance is
the conjunction of payment policy, optional prior digest, exact client commitment
and domain/type checks; no individual success flag can bypass another rejection.
The client request is mandatory and verifier absence is explicit for this bridge's
read-only evidence format. Domain match alone cannot accept an altered amount;
a matching client digest cannot accept the wrong intended chain.

One working offline command:

```sh
python3 -B shared/payment-evidence/bind.py shared/payment-evidence/example.transcript.json shared/payment-evidence/example.policy.json shared/payment-evidence/example.typed-data.json --chain-id 1 --name 'Read-only Payment Evidence' --version 1 --primary-type PaymentEvidence --no-verifier --summary
```

Exit 0, accepted historical ZTO evidence, client commitment and domain matched,
twelve trace nodes. The example's policy and client are derived demonstration
inputs, not independent approval. A consumer must supply its own policy, exact
client request and intended domain; optional prior digest needs an independent
source. This bridge accepts its own fixed read-only commitment format, not an
arbitrary application permit. Standalone domain-check serves other domains.

All twelve new tests passed, as did 26 earlier payment-bridge tests and six
original RPC-bridge tests. A detached copy passed without line folders or
external dependencies (`portable-check-04.json`). Fresh real ZTO transcript,
policy, client data and combined result are `round04.*.json`; commitment
`0x53f47d0ef21fffdaba35b3da60e8386b9d97013e77a285c6f1ca86159cef4a86`.

Re-derived the bounded capture prefix and disabled settlement transport from
mark-24 source; `provenance.json` names exact current source/copy hashes and
adaptations. An initial local rerun caught that the disabled-transport diagnostic
had lost its expected “bounded public reads” phrase. Restored that interface;
the refusing behavior and all regression tests now pass. No line source or test
was changed. Existing shared commands remain available. The old RPC bridge still
has its inherited less-strict transport; prefer payment-evidence's bounded
capture for untrusted public observations.

## Coins, scope and wall

`COINS.md` says **none**: all goals work through public reads and offline Python,
and real ZTO already provides practical payment evidence with IMD second. No new
coin, hook, pool, Sepolia contract or launch-check submission is necessary.
All four GOAL.md files are preserved and copied to `dist/goals.json`; none only
serves this cave or repeats another line. The narrowing advice above applies to
potential expansions, not replacement of the existing goals.

This is the **fourth painted gathering**, so the first-gathering placeholder
creation rule is not triggered. Record 04 replaces its inherited future slot.
Existing pending records remain exact and have no JPEGs. No line folder or line
record was changed. The single self-contained gallery includes **117 records**,
**20 paintings**, **97 future slots**, by line/wall with newest paintings first.
Local JPEG thumbnails work offline; full walls and pending cave images use the
public artifact URLs. Styles and captions are inline; no package installation,
wallet code, remote scripts, publishing or hosting step is needed.

Retrieved ancestor gathering 03 from its record and verified SHA-256
`0dd7fd645cc7f07053ecf389afd7ae96c75edd0dfc1f113e3c8e80a6cf930500`.
One installed-image-tool draft produced a charcoal eye in a worn ochre loop.
Added only its pigment on vacant stone above-left of ancestor Pepe: **5984 pixels
changed**, bounded to x **404–526**, y **179–296**; **1566532 pixels unchanged**.
Every pixel outside the 140 × 140 addition region remains identical; deep cracks
inside are protected. Ancestor paintings were neither erased, moved nor redrawn.

Full wall: **1254 × 1254 RGB PNG**, identical at `artifacts/gathering/wall.png`
and required `artifacts/gathering/wall-v4.png`. Preview: **512 × 512 JPEG**,
**75232 bytes**, `dist/gathering/04.jpg`. Record `04.json` hashes the final PNG.
`wall-review-04.json` records dimensions, formats, preservation counts and local
inspection of both the full image and decoded preview. Recognizable ancestor
Pepe retains his wide mouth and heavy-lidded eyes. Rough warm rock, cracks,
colour, torchlight, water and framing remain intact. No hands or handprints are
present, so no digits are depicted. No letters, numbers, captions, signatures,
logos, watermarks, borders, frames, real people or prohibited symbols observed.
**No known unmet visual requirements.** This is local visual review.

Delivery checking verifies image structure/CRCs, preview dimensions, SHA-256,
exact record shape/traits, placeholder coverage, copied goals, gallery ordering,
current vendored provenance, unchanged line hashes and the 100 KB cap outside
artifacts. PNG outputs remain untracked for separate daemon upload. All source
changes are confined to gathering/, shared/ and dist/.

Submission note: Git staging was attempted for gathering/, shared/ and dist/
only, but this runtime refused `.git/index.lock` with `Read-only file system`.
No commit or staging was possible here. Deliverables remain ordinary workspace
files for the daemon to collect; the required PNG is untracked as requested.
