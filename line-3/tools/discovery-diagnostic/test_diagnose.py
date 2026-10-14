"""Public error boundary and known-hash independence; all failures are fixtures."""
import io
import json
import unittest
import urllib.error
from diagnose import s, w, discover, main
from contextlib import redirect_stdout


class Opener:
    def __init__(self, value):
        self.value = value

    def open(self, request, timeout):
        if isinstance(self.value, Exception):
            raise self.value
        return io.BytesIO(self.value)


class DiagnosticTests(unittest.TestCase):
    def failure(self, value, method="eth_getLogs"):
        rpc = s.RPC(s.RPC_URL)
        rpc.opener = Opener(value)
        with self.assertRaises(s.ReadFailure) as cm:
            rpc.call(method, [])
        return cm.exception.diagnostic

    def test_http_status_without_body_or_url(self):
        body = io.BytesIO(b"fixture private upstream body")
        result = self.failure(urllib.error.HTTPError("https://fixture.invalid/private", 400,
                                                    "fixture secret reason", {}, body))
        self.assertEqual(result["method"], "eth_getLogs")
        self.assertEqual(result["code"], 400)
        self.assertEqual(result["kind"], "http")
        self.assertTrue(body.closed)
        self.assertNotIn("private", json.dumps(result))
        self.assertNotIn("secret", json.dumps(result))

    def test_connection_reason_not_echoed(self):
        result = self.failure(urllib.error.URLError("fixture credential"))
        self.assertEqual(result["kind"], "transport")
        self.assertNotIn("credential", json.dumps(result))

    def test_rpc_code_and_bounded_message_no_data(self):
        raw = json.dumps({"jsonrpc":"2.0", "id":1,
                          "error":{"code":-32005,"message":"limit\n" + "x"*5000,
                                   "data":"fixture private data"}}).encode()
        result = self.failure(raw)
        self.assertEqual(result["code"], -32005)
        self.assertEqual(len(result["detail"]), 240)
        self.assertNotIn("\n", result["detail"])
        self.assertNotIn("private", json.dumps(result))

    def test_malformed_error_fails_closed(self):
        for error in (None, "x", {"code":True,"message":"x"}, {"code":1}, {"code":1,"message":3}):
            result = self.failure(json.dumps({"jsonrpc":"2.0","id":1,"error":error}).encode())
            self.assertEqual(result["kind"], "invalid_response")

    def test_invalid_response_identifies_method(self):
        result = self.failure(b'{', "eth_chainId")
        self.assertEqual(result["method"], "eth_chainId")
        self.assertEqual(result["kind"], "invalid_response")

    def test_discovery_reports_failed_range_without_selecting_hash(self):
        class Fixture:
            def call(self, method, params):
                if method == "eth_chainId": return "0x1"
                if method == "eth_getBlockByNumber":
                    return {"number":"0x1000", "hash":w.DEMO_TX}  # synthetic block anchor
                raise s.ReadFailure(method, "http", "Public endpoint refused the read", 400)
        report, code = discover(Fixture(), 512)
        self.assertEqual(code, 2)
        self.assertEqual(report["failedRead"]["method"], "eth_getLogs")
        self.assertEqual(report["reads"][-1]["range"], {"fromBlock":"0xe01","toBlock":"0x1000"})
        self.assertNotIn("transactionHash", report)
        self.assertFalse(report["settled"])

    def test_invalid_lookback_has_no_reads(self):
        class NoReads:
            def call(self, *args): raise AssertionError("unexpected read")
        report, code = discover(NoReads(), 0)
        self.assertEqual(code, 2)
        self.assertEqual(report["reads"], [])

    def test_real_known_hash_replay_still_works(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--replay-known"])
        report = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(report["accepted"])
        self.assertEqual(report["transactionHash"], w.DEMO_TX)


if __name__ == "__main__":
    unittest.main(verbosity=2)
