#!/usr/bin/env python3
"""Offline EIP-712 domain binding against explicit caller expectations."""
import argparse
import json
import sys

from typed_digest import (TypedDataError, digest, load_workspace_json,
                          parse_hex, parse_integer, validate_tree)

DOMAIN_TYPES = {'name': 'string', 'version': 'string', 'chainId': 'uint256',
                'verifyingContract': 'address', 'salt': 'bytes32'}


def normalized(field, value):
    if field == 'chainId':
        value = parse_integer(value)
        if not 0 < value < 2**256:
            raise TypedDataError('expected chainId must be positive uint256')
        return value
    if field in ('verifyingContract', 'salt'):
        return '0x' + parse_hex(value, 20 if field == 'verifyingContract' else 32).hex()
    if type(value) is not str:
        raise TypedDataError(f'{field} expectation must be a string')
    return value


def check(data, expected_domain, primary_type, expected_digest=None):
    """No mutation or I/O. Expectations must come from a separate trusted source.

    Exact domain field coverage is intentional. An absent verifier is explicit;
    it is never silently substituted with a token or other unrelated address.
    """
    validate_tree(expected_domain)
    if type(expected_domain) is not dict:
        raise TypedDataError('expected domain must be an object')
    if not {'name', 'version', 'chainId'} <= set(expected_domain) or not set(expected_domain) <= set(DOMAIN_TYPES):
        raise TypedDataError('expect name, version, chainId and optional verifyingContract/salt only')
    if type(primary_type) is not str or not primary_type:
        raise TypedDataError('expected primary type must be a nonempty string')
    expected = {k: normalized(k, v) for k, v in expected_domain.items()}
    expected_hash = None if expected_digest is None else '0x' + parse_hex(expected_digest, 32).hex()
    calculated = digest(data)  # Validate the entire request before inspecting it.
    declarations = {f['name']: f['type'] for f in data['types']['EIP712Domain']}
    findings = []
    if data['primaryType'] != primary_type:
        findings.append({'path': '/primaryType', 'reason': 'primary type differs',
                         'expected': primary_type, 'actual': data['primaryType']})
    for field in sorted(set(declarations) | set(expected)):
        path = '/domain/' + field.replace('~', '~0').replace('/', '~1')
        if field not in expected:
            findings.append({'path': path, 'reason': 'unexpected domain field'})
        elif field not in declarations:
            findings.append({'path': path, 'reason': 'missing domain field'})
        elif declarations[field] != DOMAIN_TYPES[field]:
            findings.append({'path': '/types/EIP712Domain', 'field': field,
                             'reason': 'domain field has wrong declared type',
                             'expected': DOMAIN_TYPES[field], 'actual': declarations[field]})
        else:
            # Zero is encodable, but never matches a positive expected chain.
            actual = (parse_integer(data['domain'][field]) if field == 'chainId'
                      else normalized(field, data['domain'][field]))
            if actual != expected[field]:
                findings.append({'path': path, 'reason': 'domain value differs',
                                 'expected': expected[field], 'actual': actual})
    domain_matches = not findings
    matches_digest = None if expected_hash is None else expected_hash == calculated['digest']
    if matches_digest is False:
        findings.append({'path': '/digest', 'reason': 'digest differs',
                         'expected': expected_hash, 'actual': calculated['digest']})
    return {'accepted': not findings, 'domainAndPrimaryTypeMatch': domain_matches,
            'matchesExpectedDigest': matches_digest, **calculated,
            'expectedDomain': expected, 'expectedPrimaryType': primary_type,
            'domainFieldOrder': list(declarations),
            'verifierBinding': 'checked' if 'verifyingContract' in expected else 'explicitly absent',
            'differences': findings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='workspace JSON, <=65536 bytes; no hidden paths or symlinks')
    parser.add_argument('--chain-id', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--primary-type', required=True)
    verifier = parser.add_mutually_exclusive_group(required=True)
    verifier.add_argument('--verifier', help='independently known verifying contract, not the token by default')
    verifier.add_argument('--no-verifier', action='store_true', help='require verifyingContract to be absent')
    parser.add_argument('--salt', help='require this exact bytes32 salt; otherwise require absence')
    parser.add_argument('--expect', help='independently supplied expected digest; otherwise only domain/type are pinned')
    args = parser.parse_args(argv)
    try:
        expected = {'name': args.name, 'version': args.version, 'chainId': args.chain_id}
        if args.verifier is not None:
            expected['verifyingContract'] = args.verifier
        if args.salt is not None:
            expected['salt'] = args.salt
        result = check(load_workspace_json(args.input), expected, args.primary_type, args.expect)
        print(json.dumps(result, indent=2))
        return 0 if result['accepted'] else 1
    except (ValueError, OSError, RecursionError) as exc:
        print(f'domain-check: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
