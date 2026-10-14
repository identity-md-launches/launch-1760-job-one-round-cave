"""Cross-line acceptance gates over the actual saved historical ZTO transcript."""
import contextlib
import copy
import io
import json
from pathlib import Path
import unittest

from bind import bind_payment, main
from check import check, load

HERE = Path(__file__).resolve().parent
DOMAIN = {'name': 'Read-only Payment Evidence', 'version': '1', 'chainId': 1}


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.sample = load(HERE / 'example.transcript.json')
        self.policy = load(HERE / 'example.policy.json')
        checked = check(self.sample, self.policy)
        self.client = checked['typedData']
        self.digest = checked['commitment']['digest']

    def run_bind(self, domain=None, primary='PaymentEvidence', digest=None, summary=True):
        return bind_payment(self.sample, self.policy, self.client,
                            DOMAIN if domain is None else domain, primary, digest, summary)

    def test_historical_zto_round_trip(self):
        r = self.run_bind(digest=self.digest)
        self.assertTrue(r['accepted'])
        self.assertTrue(r['paymentAccepted'])
        self.assertTrue(r['comparison']['matchesCommitment'])
        self.assertTrue(r['domainBinding']['accepted'])
        self.assertFalse(r['providerAuthenticated'])
        self.assertEqual(r['traceNodes'], 12)

    def test_correct_digest_wrong_intended_chain_rejected(self):
        r = self.run_bind({**DOMAIN, 'chainId': 2}, digest=self.digest)
        self.assertTrue(r['comparison']['matchesCommitment'])
        self.assertTrue(r['domainBinding']['matchesExpectedDigest'])
        self.assertFalse(r['accepted'])
        self.assertEqual(r['domainBinding']['differences'][0]['path'], '/domain/chainId')

    def test_wrong_expected_name_version_or_primary_rejected(self):
        for field in ('name', 'version'):
            with self.subTest(field=field):
                self.assertFalse(self.run_bind({**DOMAIN, field: 'other'})['accepted'])
        self.assertFalse(self.run_bind(primary='OtherEvidence')['accepted'])

    def test_verifier_must_be_explicitly_absent_for_content_commitment(self):
        r = self.run_bind({**DOMAIN, 'verifyingContract': self.client['message']['token']})
        self.assertFalse(r['accepted'])
        self.assertEqual(r['domainBinding']['verifierBinding'], 'checked')

    def test_domain_match_does_not_accept_altered_message(self):
        self.client['message']['minimumRaw'] = '1'
        r = self.run_bind()
        self.assertTrue(r['domainBinding']['accepted'])
        self.assertTrue(r['paymentAccepted'])
        self.assertFalse(r['comparison']['matchesCommitment'])
        self.assertFalse(r['accepted'])

    def test_wrong_prior_digest_is_rejected(self):
        r = self.run_bind(digest='0x' + '12'*32)
        self.assertFalse(r['accepted'])
        self.assertFalse(r['matchesExpectedDigest'])
        self.assertFalse(r['domainBinding']['matchesExpectedDigest'])

    def test_domain_and_encoding_cannot_bypass_payment_shortfall(self):
        self.policy['minimum_raw'] = str(int(self.policy['minimum_raw']) + 1)
        self.sample['policy'] = copy.deepcopy(self.policy)
        self.client = check(self.sample, self.policy)['typedData']
        r = self.run_bind()
        self.assertTrue(r['comparison']['matchesCommitment'])
        self.assertTrue(r['domainBinding']['accepted'])
        self.assertFalse(r['paymentAccepted'])
        self.assertFalse(r['accepted'])

    def test_transcript_cannot_lower_independent_policy(self):
        self.sample['policy']['minimum_raw'] = '1'
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_invalid_domain_and_client_fail(self):
        for domain in ({}, {**DOMAIN, 'chainId': True}, {**DOMAIN, 'extra': 1}):
            with self.subTest(domain=domain), self.assertRaises(ValueError):
                self.run_bind(domain)
        del self.client['message']['token']
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_no_mutation_and_full_summary_same_decision(self):
        before = copy.deepcopy((self.sample, self.policy, self.client, DOMAIN))
        full = self.run_bind(summary=False)
        short = self.run_bind()
        self.assertEqual(full['accepted'], short['accepted'])
        self.assertEqual(full['commitment'], short['commitment'])
        self.assertEqual(len(full['encodingTrace']['nodes']), short['traceNodes'])
        self.assertEqual((self.sample, self.policy, self.client, DOMAIN), before)

    def test_equivalent_chain_representation(self):
        self.assertTrue(self.run_bind({**DOMAIN, 'chainId': '0x01'})['accepted'])

    def test_cli_success_mismatch_invalid_input(self):
        args = [str(HERE / 'example.transcript.json'), str(HERE / 'example.policy.json'),
                str(HERE / 'example.typed-data.json'), '--chain-id', '1',
                '--name', DOMAIN['name'], '--version', '1', '--primary-type',
                'PaymentEvidence', '--no-verifier', '--summary']
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(args), 0)
        self.assertTrue(json.loads(out.getvalue())['accepted'])
        args[4] = '2'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(args), 1)
        args[0] = '../outside.json'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(args), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
