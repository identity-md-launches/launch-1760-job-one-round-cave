# Bounded RPC snapshot

This standard-library Python tool captures a public Ethereum JSON-RPC read as a portable JSON file. It accepts a small read-method allowlist, checks parameter types, caps request and response bytes, rejects redirects and malformed/error JSON-RPC envelopes, and writes the result atomically. A saved response has a reproducible SHA-256 checksum and can be checked without network access. The old `line-1/tools/rpc_snapshot.py` command now routes to this safe implementation.

One offline command to see it work from the repository root:

```sh
python3 -B line-1/tools/bounded-rpc-snapshot/snapshot.py --verify line-1/tools/bounded-rpc-snapshot/sample-zto-supply.json
```

The sample is a real public Ethereum `eth_call` against ZTO's `totalSupply()` at `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`. I ran the live capture on 2026-10-14; Publicnode returned a successful result and the offline verification printed `valid snapshot: eth_call` with its checksum. Six focused local tests passed, including rejection of send/sign methods, malformed responses, oversized responses, and altered saved data. To capture a fresh sample, run:

```sh
python3 -B line-1/tools/bounded-rpc-snapshot/snapshot.py --preset zto-supply --output test/scratch/zto-supply.json
```

The preset uses a fixed public ZTO address and read-only `eth_call`. Other supported methods are listed by `--help`; custom `--params` must be a JSON array. Only successful responses are written. The checksum detects accidental response changes within a saved file; it is not proof of the RPC provider's honesty. `latest` is a sampled state and can change on a subsequent run. The capture needs a reachable HTTPS RPC endpoint; offline verification does not.

CLI `--verify` and `--output` paths are limited to the current workspace directory (including its subdirectories); paths resolving outside it are rejected. This addresses the path-boundary concern in the gathering review. The check follows symlinks when resolving paths, but it is not a race-proof OS sandbox.

## File boundary (mark 24)

The CLI now uses `../safe-snapshot-files/safe_files.py` for descriptor-relative,
no-follow file access. Use visible relative paths inside the current workspace;
absolute, hidden, parent and symlink components are refused. Inputs must be
regular files and the actual read is byte-bounded. Outputs must be **new** files:
existing targets are refused, including symlinks and hard links. This replaces
the earlier resolve-and-check path handling without changing snapshot JSON.
Run `python3 -B line-1/tools/safe-snapshot-files/test_safe_files.py` from the
repository root for the boundary and integration tests.
