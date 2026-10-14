#!/usr/bin/env python3
"""Bind replayed payment evidence and client encoding to caller domain expectations."""
import argparse
import json
import sys

from explain import explain_payment
from check import load
from domain_check import check as check_domain


def bind_payment(sample, policy, client, expected_domain, primary_type,
                 expect_digest=None, summary=False):
    """Require payment, client commitment and independent domain/type to all match."""
    payment = explain_payment(sample, policy, client, expect_digest, summary)
    binding = check_domain(client, expected_domain, primary_type, expect_digest)
    return {**payment,
            'accepted': payment['accepted'] and binding['accepted'],
            'domainBinding': binding,
            'authorization': 'Read-only content check; no signing or token permit.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('transcript')
    parser.add_argument('policy', help='independently chosen payment policy')
    parser.add_argument('client', help='exact client typed-data request')
    parser.add_argument('--chain-id', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--primary-type', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--verifier')
    group.add_argument('--no-verifier', action='store_true')
    parser.add_argument('--salt')
    parser.add_argument('--expect-digest', help='independently obtained complete commitment')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args(argv)
    expected = {'chainId': args.chain_id, 'name': args.name, 'version': args.version}
    if args.verifier is not None:
        expected['verifyingContract'] = args.verifier
    if args.salt is not None:
        expected['salt'] = args.salt
    try:
        result = bind_payment(load(args.transcript), load(args.policy), load(args.client),
                              expected, args.primary_type, args.expect_digest, args.summary)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0 if result['accepted'] else 1
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'accepted': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
