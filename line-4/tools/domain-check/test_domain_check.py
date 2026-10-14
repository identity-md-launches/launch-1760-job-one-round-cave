"""Offline adversarial domain binding tests; standard library only."""
import contextlib
import copy
import io
import json
from pathlib import Path
import unittest

from domain_check import check, main
from typed_digest import TypedDataError, loads_bounded

EXAMPLE = str(Path(__file__).resolve().parent / 'zto-payment.json')
EXPECTED = {'name': 'Read-only Payment Evidence', 'version': '1', 'chainId': 1}
HASH = '0xf33e2506e5c103f98dbfe3feb6d4b87d55f1fad4e423dbaa8462465ff4ab9774'
ZTO = '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.data = loads_bounded(Path(EXAMPLE).read_bytes())

    def run_check(self, expected=None, primary='PaymentEvidence', expected_hash=HASH):
        return check(self.data, EXPECTED if expected is None else expected, primary, expected_hash)

    def test_real_observation_commitment(self):
        r = self.run_check()
        self.assertTrue(r['accepted'])
        self.assertEqual(r['digest'], HASH)
        self.assertEqual(r['verifierBinding'], 'explicitly absent')

    def test_chain_mismatch_even_when_digest_matches(self):
        r = self.run_check({**EXPECTED, 'chainId': 2})
        self.assertFalse(r['accepted'])
        self.assertTrue(r['matchesExpectedDigest'])
        self.assertEqual(r['differences'][0]['path'], '/domain/chainId')

    def test_missing_chain(self):
        self.data['types']['EIP712Domain'].pop()
        del self.data['domain']['chainId']
        r = self.run_check(expected_hash=None)
        self.assertFalse(r['accepted'])
        self.assertEqual(r['differences'][0]['reason'], 'missing domain field')

    def test_wrong_chain_type_same_visible_value(self):
        self.data['types']['EIP712Domain'][2]['type'] = 'string'
        self.data['domain']['chainId'] = '1'
        r = self.run_check(expected_hash=None)
        self.assertFalse(r['accepted'])
        self.assertEqual(r['differences'][0]['reason'], 'domain field has wrong declared type')

    def test_wrong_integer_width_same_hash(self):
        self.data['types']['EIP712Domain'][2]['type'] = 'uint8'
        self.assertFalse(self.run_check(expected_hash=None)['accepted'])

    def test_extra_domain_field(self):
        self.data['types']['EIP712Domain'].append({'name': 'network', 'type': 'string'})
        self.data['domain']['network'] = 'Ethereum'
        self.assertFalse(self.run_check(expected_hash=None)['accepted'])

    def test_name_and_version(self):
        for field in ('name', 'version'):
            with self.subTest(field=field):
                r = self.run_check({**EXPECTED, field: 'different'})
                self.assertFalse(r['accepted'])
                self.assertTrue(r['matchesExpectedDigest'])

    def test_explicit_absence_rejects_present_verifier(self):
        self.add_verifier()
        self.assertFalse(self.run_check(expected_hash=None)['accepted'])

    def add_verifier(self):
        # Synthetic verifier-binding variation; NOT a ZTO permit claim.
        self.data['types']['EIP712Domain'].append({'name': 'verifyingContract', 'type': 'address'})
        self.data['domain']['verifyingContract'] = ZTO

    def test_required_verifier_missing(self):
        self.assertFalse(self.run_check({**EXPECTED, 'verifyingContract': ZTO})['accepted'])

    def test_address_case_is_encoding_equivalent(self):
        self.add_verifier()
        expected = {**EXPECTED, 'verifyingContract': '0x' + ZTO[2:].upper()}
        r = self.run_check(expected, expected_hash=None)
        self.assertTrue(r['accepted'])
        self.assertEqual(r['verifierBinding'], 'checked')

    def test_wrong_verifier(self):
        self.add_verifier()
        expected = {**EXPECTED, 'verifyingContract': '0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7'}
        self.assertFalse(self.run_check(expected, expected_hash=None)['accepted'])

    def test_salt_exact_and_absence(self):
        salt = HASH
        self.data['types']['EIP712Domain'].append({'name': 'salt', 'type': 'bytes32'})
        self.data['domain']['salt'] = salt
        self.assertFalse(self.run_check(expected_hash=None)['accepted'])
        self.assertTrue(self.run_check({**EXPECTED, 'salt': salt}, expected_hash=None)['accepted'])
        self.assertFalse(self.run_check({**EXPECTED, 'salt': '0x' + '11'*32}, expected_hash=None)['accepted'])

    def test_numeric_chain_representations(self):
        for value in ('1', '0x01', 1):
            self.data['domain']['chainId'] = value
            self.assertTrue(self.run_check()['accepted'])

    def test_zero_chain_does_not_match(self):
        self.data['domain']['chainId'] = 0
        self.assertFalse(self.run_check(expected_hash=None)['accepted'])

    def test_invalid_expectations(self):
        for value in (0, -1, True, 1.0, 'bogus', 2**256):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_check({**EXPECTED, 'chainId': value})
        for expected in ({}, {**EXPECTED, 'extra': 'x'}, [], {**EXPECTED, 'verifyingContract': '0x1'}):
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                self.run_check(expected)
        with self.assertRaises(ValueError):
            self.run_check(primary='')
        with self.assertRaises(ValueError):
            self.run_check(expected_hash='0x1')

    def test_primary_type_mismatch(self):
        self.assertFalse(self.run_check(primary='TokenNote')['accepted'])

    def test_message_edit_only_detected_by_digest(self):
        self.data['message']['minimumRaw'] = '1'
        r = self.run_check()
        self.assertTrue(r['domainAndPrimaryTypeMatch'])
        self.assertFalse(r['accepted'])
        self.assertTrue(self.run_check(expected_hash=None)['accepted'])

    def test_reordered_domain_is_valid_but_changes_digest(self):
        self.data['types']['EIP712Domain'].reverse()
        r = self.run_check()
        self.assertTrue(r['domainAndPrimaryTypeMatch'])
        self.assertFalse(r['matchesExpectedDigest'])
        self.assertTrue(self.run_check(expected_hash=None)['accepted'])

    def test_invalid_request_not_a_policy_mismatch(self):
        del self.data['message']['minimumRaw']
        with self.assertRaises(TypedDataError):
            self.run_check()

    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            loads_bounded(b'{"domain": {}, "domain": {}}')

    def test_inputs_immutable(self):
        before = copy.deepcopy(self.data)
        expected = copy.deepcopy(EXPECTED)
        self.run_check(expected)
        self.assertEqual(self.data, before)
        self.assertEqual(expected, EXPECTED)

    def test_cli_codes(self):
        args = [EXAMPLE, '--chain-id', '1', '--name', EXPECTED['name'], '--version', '1',
                '--primary-type', 'PaymentEvidence', '--no-verifier', '--expect', HASH]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(args), 0)
        self.assertTrue(json.loads(output.getvalue())['accepted'])
        args[2] = '2'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(args), 1)
        args[2] = 'true'
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(args), 2)
        args[0] = '../outside.json'
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(args), 2)


if __name__ == '__main__':
    unittest.main()
