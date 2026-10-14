#!/usr/bin/env python3
"""Capture and check a finalized, block-anchored ZTO totalSupply RPC bundle."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys


BOUNDED = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                             "bounded-rpc-snapshot" / "snapshot.py"))
RPC_URL = BOUNDED["DEFAULT_RPC"]
ZTO = BOUNDED["ZTO"]
SCHEMA = "line1-anchored-zto-supply-v1"
HEX_64 = re.compile(r"^0x[0-9a-fA-F]{64}$")
HEX_QUANTITY = re.compile(r"^0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)$")
REQUIRED_BUNDLE = {"schema", "rpc_url", "captured_at_utc", "reads"}
REQUIRED_READ = {"method", "params", "content_type", "response", "response_sha256"}
MAX_FILE = 500_000


class BundleError(Exception):
    """The bundle is malformed or its four observations do not agree."""


def require(condition, message):
    if not condition:
        raise BundleError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def quantity(value):
    require(isinstance(value, str) and HEX_QUANTITY.fullmatch(value),
            "invalid hex quantity")
    return int(value, 16)


def result_of(read):
    response = read["response"]
    require("result" in response, "RPC read has no result")
    return response["result"]


def validate_read(read):
    require(isinstance(read, dict) and set(read) == REQUIRED_READ,
            "read fields differ from schema")
    require(isinstance(read["content_type"], str) and
            len(read["content_type"]) <= 200, "invalid content type")
    BOUNDED["validate_request"](read["method"], read["params"])
    BOUNDED["validate_response"](read["response"])
    require(isinstance(read["response_sha256"], str) and
            re.fullmatch(r"[0-9a-f]{64}", read["response_sha256"]) and
            digest(read["response"]) == read["response_sha256"],
            "RPC response checksum mismatch")


def validate_bundle(bundle):
    require(isinstance(bundle, dict) and set(bundle) == REQUIRED_BUNDLE,
            "bundle fields differ from schema")
    require(bundle["schema"] == SCHEMA and bundle["rpc_url"] == RPC_URL,
            "wrong schema or RPC URL")
    require(isinstance(bundle["captured_at_utc"], str) and
            len(bundle["captured_at_utc"]) <= 64, "invalid capture time")
    try:
        captured = datetime.fromisoformat(bundle["captured_at_utc"])
    except ValueError as exc:
        raise BundleError("invalid capture time") from exc
    require(captured.tzinfo is not None, "capture time needs timezone")
    reads = bundle["reads"]
    require(isinstance(reads, list) and len(reads) == 4,
            "bundle requires four ordered RPC reads")
    for read in reads:
        validate_read(read)
    chain, first_block, supply, last_block = reads
    require(chain["method"] == "eth_chainId" and chain["params"] == [],
            "first read must be chain ID")
    require(result_of(chain) == "0x1", "provider did not report Ethereum mainnet")
    require(first_block["method"] == "eth_getBlockByNumber" and
            first_block["params"] == ["finalized", False],
            "second read must be finalized block")
    block = result_of(first_block)
    require(isinstance(block, dict), "finalized block missing")
    block_number = block.get("number")
    block_hash = block.get("hash")
    quantity(block_number)
    require(isinstance(block_hash, str) and HEX_64.fullmatch(block_hash),
            "finalized block hash missing")
    require(supply["method"] == "eth_call" and
            supply["params"] == [{"to": ZTO, "data": "0x18160ddd"}, block_number],
            "third read must query ZTO supply at the finalized block")
    raw_supply = result_of(supply)
    require(isinstance(raw_supply, str) and HEX_64.fullmatch(raw_supply),
            "ZTO totalSupply response is not one uint256 word")
    require(last_block["method"] == "eth_getBlockByNumber" and
            last_block["params"] == [block_number, False],
            "fourth read must recheck the same block")
    rechecked = result_of(last_block)
    require(isinstance(rechecked, dict) and
            rechecked.get("number") == block_number and
            rechecked.get("hash") == block_hash,
            "block changed between reads")
    return {"block_number": quantity(block_number),
            "block_hash": block_hash,
            "zto_total_supply_raw": int(raw_supply, 16)}


def capture(timeout):
    def read(method, params):
        content_type, response = BOUNDED["rpc_call"](
            RPC_URL, method, params, timeout)
        return {"method": method, "params": params,
                "content_type": content_type, "response": response,
                "response_sha256": digest(response)}

    chain = read("eth_chainId", [])
    first_block = read("eth_getBlockByNumber", ["finalized", False])
    block = result_of(first_block)
    require(isinstance(block, dict) and isinstance(block.get("number"), str),
            "finalized block missing")
    block_number = block["number"]
    supply = read("eth_call", [{"to": ZTO, "data": "0x18160ddd"}, block_number])
    last_block = read("eth_getBlockByNumber", [block_number, False])
    bundle = {"schema": SCHEMA, "rpc_url": RPC_URL,
              "captured_at_utc": datetime.now(timezone.utc).isoformat(),
              "reads": [chain, first_block, supply, last_block]}
    return bundle, validate_bundle(bundle)


def workspace_path(raw, writing=False):
    BOUNDED["SAFE_FILES"]["parts"](raw)
    return raw


def verify(path):
    raw = BOUNDED["SAFE_FILES"]["read_bytes"](path, MAX_FILE)
    bundle = BOUNDED["parse_json"](raw)
    return validate_bundle(bundle)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", help="capture bundle to a workspace JSON file")
    action.add_argument("--verify", help="check a saved workspace JSON file offline")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args(argv)
    try:
        if args.verify:
            info = verify(workspace_path(args.verify))
        else:
            require(0 < args.timeout <= 60, "timeout must be within (0, 60] seconds")
            output = workspace_path(args.output, writing=True)
            bundle, info = capture(args.timeout)
            rendered = json.dumps(bundle, indent=2, sort_keys=True) + "\n"
            require(len(rendered.encode()) <= MAX_FILE, "bundle exceeds byte limit")
            BOUNDED["write_snapshot"](output, rendered)
        print(f"ZTO supply at finalized block {info['block_number']}: "
              f"{info['zto_total_supply_raw']} raw units "
              f"(hash {info['block_hash']})")
        return 0
    except (BundleError, BOUNDED["SnapshotError"], OSError, ValueError) as exc:
        print(f"anchored-zto-snapshot: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
