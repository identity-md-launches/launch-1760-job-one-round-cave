# Bounded JSON contract checker

Validate one or more JSON deliverables against a trusted explicit structural
contract, offline, with bounded workspace file reads. Python 3.10+, standard
library only, on POSIX systems with `O_NOFOLLOW` and directory descriptor support.
Keep the sibling `json-contract` folder: this entry point reuses its unchanged
validation engine, including ordered items and precise JSON Pointer errors.

One command from the repository root shows it working on actual inherited files:

```sh
python3 -B line-2/tools/bounded-contract/check.py line-2/tools/ordered-deliverables/record.strict.contract.json dist/line-2/01.json dist/line-2/22.json dist/line-2/23.json
```

The result reports three passed, zero failed and zero unreadable; exit 0.
Rows preserve input order and checking continues after an unreadable document.
Exit 1 means a structural violation; exit 2 means an invalid contract or any
unreadable/malformed document. The contract is prepared once. Up to 256 documents
are accepted per invocation. The program writes nothing, contacts no service,
and does not read configuration, environment variables, keys or wallets.

## The file boundary

Use relative paths inside the current workspace. Absolute paths, empty path
components, parent traversal, hidden components, and symlinks in any component
are refused. Each directory is opened relative to the preceding open directory
with `O_DIRECTORY | O_NOFOLLOW`. The leaf uses `O_NOFOLLOW | O_NONBLOCK` and
`fstat` must identify a regular file. This refuses FIFO inputs without waiting
for a writer and prevents symlink replacement from redirecting a read.
Directory descriptors remain pinned if an ancestor pathname is replaced.

The reader checks the open file's size, then reads at most 1,000,001 bytes to
enforce the 1,000,000-byte cap even if the file grows. Short reads are joined.
Descriptors close on success and on error. UTF-8 decoding, duplicate-key refusal
and finite-number parsing happen only after a bounded read. The trusted sibling
engine source is loaded through this same boundary, without generating bytecode.
The inherited checkers remain available with their original interfaces.

## What happened when tried

The demonstration passed all three real records. All 14 new regression tests
passed, together with the inherited engine's 10 and ordered checker's 13 tests.
Tests exercise exact/over-limit reads, simulated growth after `fstat`, short
reads, symlinks at leaf and directory positions, FIFO refusal, directory
replacement, descriptor cleanup, malformed UTF-8, duplicate/nonfinite JSON,
JSON Pointer violations and exit-code precedence across mixed inputs.
Fixtures are created and removed only under `test/scratch/`.

```sh
python3 -B line-2/tools/bounded-contract/test_check.py
```

## Limits

This closes the file-reader gap identified in the gathering report for callers
using this entry point. It is not a full operating-system sandbox: the workspace
and tool code must be trusted; hard links and mounted directories are not
excluded. A file edited in place during a read can yield mixed content, although
it cannot defeat the byte cap. It does not prove provenance, facts, or authenticity.
Contracts and regular expressions must be trusted; the existing regex and
quadratic uniqueness resource limits are unchanged. The small contract language
is not full JSON Schema. Windows is unsupported. No coin is needed for offline
structural validation.

## Wall

Mark: **Stone Sieve**. Pepe keeps unsafe stones outside the sieve before checking
their shapes. The wall and record details, dimensions, formats, preservation
comparison and visual review are recorded in `validation.json` beside this file.
The generation prompt and local finishing method are in `wall-method.md`.
