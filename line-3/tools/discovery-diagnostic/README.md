# Discovery diagnostic

Find a recent real ZTO transfer using bounded public Ethereum reads, and identify
the read that failed when discovery cannot finish. This standard-library Python
piece repairs the gathering report's missing failure context. It is useful to
workers deciding whether an endpoint problem prevented discovery before any
settlement check could run.

From the repository root, one fully offline command demonstrates the independent
known-hash path against inherited real ZTO evidence:

```sh
python3 -B line-3/tools/discovery-diagnostic/diagnose.py --replay-known
```

It exits 0 with `accepted: true`. The expected recipient and amount in this demo
come from the saved observation, so it demonstrates historical decoding and
settlement replay rather than an independently supplied invoice or current chain
state. It reuses the unchanged payment-witness policy code and reads only the
workspace's committed `live-evidence.json`.

Live discovery (no wallet, signing, payments or sends):

```sh
python3 -B line-3/tools/discovery-diagnostic/diagnose.py --discover --lookback 512
```

The default is publicnode; `--rpc https://eth.drpc.org` selects the second public
endpoint. Lookback is 1–16384 blocks in queries of at most 512 blocks: at most
34 reads including chain ID and latest block. No retries or timers run. The
transport uses its own User-Agent, refuses redirects and disables proxy discovery.
Discovery exit 0 means a **candidate**, never a settled transaction. Exit 2 means
discovery failed; no replacement hash is selected. Use a hash independently known
to you with the existing settlement checker:

```sh
python3 -B line-3/tools/settlement-check/settlement.py --tx YOUR_TRANSACTION_HASH --require-finalized
```

`YOUR_TRANSACTION_HASH` is an explicit input instruction, not a runnable default.
Settlement exits 0 for settled, 1 for unmet policy, 2 for errors.

## What changed and what happened

The shared settlement RPC now raises `ReadFailure`, still an `EvidenceError`,
with the exact allowed method and failure kind. HTTP failures expose only status
code and a fixed explanation; connection failures omit internal exception text.
JSON-RPC failures expose an integer code and a printable, 240-character maximum
provider message, excluding `data`. Invalid replies have bounded diagnostics.
Endpoint URLs, HTTP bodies and request parameters are not copied into errors.
The settlement CLI includes a structured `failedRead` object, so its existing
`--latest-zto-transfer` entry point benefits too. Successful results and finality
policy are unchanged. Discovery adds completed/failed method steps and the public
block range for log queries.

On 2026-10-14, direct publicnode discovery succeeded and returned real ZTO hash
`0x1d4216735d8463fc5803defb7a691582ba08b44ce4a9e391071b54044de051db`.
`live-discovery.json` records the actual queried range and method outcomes.
Its settlement check (`live-settlement.json`) correctly exited 1:
execution succeeded with 20 confirmations, but the inclusion at 26192185 was
above finalized head 26192133. No polling or invented fallback was used.
The historical known transaction also passed a fresh finalized ZTO payment
check; `live-known-payment.json` saves that separate observation and transcript.
This successful direct-endpoint trial does not establish the cause of the earlier
gathering runtime's HTTP 400.

The eight new tests passed, along with all 42 inherited checks. Run the new
boundary checks without network:

```sh
python3 -B -m unittest discover -s line-3/tools/discovery-diagnostic -p 'test_*.py'
```

Tests deliberately simulate HTTP 400, connection failures, malformed RPC errors,
oversized/control-character messages and a failed log-query range; the real
known-hash replay succeeds independently. These simulated failures are test
fixtures, not claims about a live provider.

## Limits

This is provider evidence, not a cryptographic receipt/consensus proof. Provider
messages are untrusted text, even when bounded. Saved reports do not prove
provenance or freshness. A discovery result needs separate canonical settlement
and payment-policy checks; neither a transaction hash nor a successful execution
proves that an invoice was paid. ZTO is the discovery token; the inherited payment
witness supports IMD second. No external package or extra coin is needed.
