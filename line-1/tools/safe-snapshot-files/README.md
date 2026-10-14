# Safe snapshot files

Pepe weaves a boundary that keeps public evidence safely contained.

This standard-library Python piece makes portable public Ethereum snapshots safer to read and save. It repairs the path-boundary weakness noted in the gathering review and is integrated into both the bounded snapshot CLI and the anchored ZTO CLI. It uses POSIX directory descriptors and `O_NOFOLLOW` for each path component, accepts only ordinary visible relative workspace paths, refuses symlinks and nonregular inputs, and bounds the bytes actually read. A replacement of a directory pathname cannot redirect an already-open descriptor. Publishing uses an atomic no-clobber link: a complete new file appears, or an existing file is left intact. No wallet, signature or transaction is used.

From the repository root, one offline command demonstrates the working piece, including replay of actual ZTO observations:

```sh
python3 -B line-1/tools/safe-snapshot-files/test_safe_files.py
```

**Tried on 2026-10-14:** all 19 tests passed. They cover actual saved ZTO evidence, path rejection, exact and exceeded byte limits, symlink leaves and ancestors, nonblocking FIFO rejection, directories, nested output, refusal to overwrite regular/symlink/hardlink targets, cleanup, deterministic directory and leaf replacement races, a real bundle round trip, checksum tampering and both CLI integrations. A first test run exposed a test that expected the wrong exception class for checksum tampering; correcting that assertion made the suite pass without weakening the implementation.

A fresh four-read Ethereum capture also succeeded using this machine's assigned transport for the public source `https://ethereum-rpc.publicnode.com`. It observed finalized block **26192037**, hash `0xf77b9d4a3950ac27c46984218dd2e4a4c02976bbe20957119608c8e203ee9f94`, and real ZTO total supply **1000000000000000000000000000** raw units. `live-zto.json` was written through the new boundary and verified offline immediately. Replay it with:

```sh
python3 -B line-1/tools/anchored-zto-snapshot/anchored.py --verify line-1/tools/safe-snapshot-files/live-zto.json
```

Inspect any visible workspace file through the bounded reader:

```sh
python3 -B line-1/tools/safe-snapshot-files/safe_files.py line-1/tools/safe-snapshot-files/live-zto.json
```

Existing capture commands still work. Choose a **new** relative output filename every time; existing targets are deliberately refused rather than replaced. Absolute paths, `.`/`..`, empty components and hidden components are refused. Existing saved evidence formats are unchanged. The Python implementation uses only the standard library; the test suite writes temporary fixtures only under `test/scratch/`.

Limits: POSIX no-follow/descriptors/hard links must be supported; unsupported platforms fail closed. The current workspace directory and trusted tool source are the starting boundary. Reading a hard-linked ordinary input does not prove its provenance. Other writers may mutate an already-open regular input; checksums and semantic replay still matter. Output directory contents must not be controlled by a hostile peer during publication: no-follow traversal is not isolation from a peer that can replace temporary files or remove completed files. Directory renaming may mean a completed output resides in the originally opened directory at its new name; it will never follow the substituted symlink. This is file-handling protection, not a sandbox or Ethereum state proof. Snapshot evidence continues to trust its RPC provider and cannot authenticate provenance or freshness merely through a checksum. Block-number calls plus a hash recheck remain the inherited protocol. No new coin is needed.
