# Anchored ZTO snapshot

This standard-library Python tool turns four public Ethereum JSON-RPC reads into one portable, offline-readable JSON bundle. It reads the Ethereum chain ID, a finalized block, ZTO `totalSupply()` at that block number, and the same block again. The second block read must have the same hash. The bundle retains each raw JSON-RPC response and its SHA-256 checksum. Offline verification checks the read order, mainnet ID, ZTO address and call selector, block agreement, response shapes, and checksums.

From the repository root, one command shows the saved real-chain example working without network access:

```sh
python3 -B line-1/tools/anchored-zto-snapshot/anchored.py --verify line-1/tools/anchored-zto-snapshot/sample.json
```

I captured `sample.json` from `https://ethereum-rpc.publicnode.com` on 2026-10-14. The live capture and offline verification both succeeded: finalized block 26191749, hash `0x6c211d7b0276347d6edad74ed78044a6d38cfd065d4983455b4c3e018a0654fa`, ZTO raw total supply `1000000000000000000000000000`. The file is 53,226 bytes. To capture a new bundle:

```sh
python3 -B line-1/tools/anchored-zto-snapshot/anchored.py --output test/scratch/zto-finalized.json
```

The tool uses the bounded read transport in `../bounded-rpc-snapshot/snapshot.py`. It only accepts input/output paths inside the current workspace. It never reads a wallet, signs, or sends a transaction. Verification detects accidental response changes when the stored checksum is unchanged and inconsistent observations; it does not prove the RPC provider's honesty or independently establish consensus finality. The supply is reported in raw token units. The capture needs a reachable public RPC endpoint; verification does not.

## File boundary (mark 24)

Saved bundle reads and output now pass through the shared safe snapshot files
piece. Supply visible relative workspace paths; no hidden, parent, absolute or
symlink components are accepted. Inputs are byte-bounded regular files. Output
uses an atomic no-clobber publication, so choose a **new** filename for every
capture. See `../safe-snapshot-files/README.md` for the replacement-race tests,
POSIX requirements and remaining trust limits. Bundle JSON and semantic checks
are unchanged.
