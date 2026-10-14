#!/usr/bin/env python3
"""One-shot public-read trials. Optional runtime routing is supplied by the caller."""
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = 'https://ethereum-rpc.publicnode.com'


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    if Path.cwd().resolve() != ROOT:
        raise SystemExit('Run from the repository root')
    snapshot = module('live_snapshot', 'line-1/tools/bounded-rpc-snapshot/snapshot.py')
    anchored = module('live_anchored', 'line-1/tools/anchored-zto-snapshot/anchored.py')
    witness = module('live_witness', 'line-3/tools/payment-witness/witness.py')
    diagnostic = module('live_diagnostic', 'line-3/tools/discovery-diagnostic/diagnose.py')
    results = []
    trials = [
        ('line1 bounded ZTO supply', snapshot.main, ['--preset', 'zto-supply']),
        ('line1 finalized ZTO bundle', anchored.main,
         ['--output', 'gathering/anchored-round04.json']),
        ('line3 diagnostic ZTO discovery', diagnostic.main,
         ['--discover', '--lookback', '512']),
        ('line3 known-hash real ZTO payment', witness.main, ['--demo'])]
    for label, function, args in trials:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = function(args)
        output = out.getvalue()
        row = {'trial': label, 'source': PUBLIC, 'exitCode': code,
               'stdout': output, 'stderr': err.getvalue()}
        if label == 'line3 known-hash real ZTO payment' and code == 0:
            report = json.loads(output)
            sample = report.pop('sample')
            bridge = ROOT / 'shared/payment-evidence'
            for suffix, value in [('transcript', sample), ('policy', sample['policy'])]:
                (bridge / f'round04.{suffix}.json').write_text(json.dumps(value, indent=2)+'\n')
            row['stdout'] = json.dumps(report, indent=2)
        results.append(row)
        print(label, 'exit', code, flush=True)
    (ROOT / 'gathering/live-check-results-04.json').write_text(json.dumps(results, indent=2)+'\n')
    return 0 if all(row['exitCode'] == 0 for row in results) else 1


if __name__ == '__main__':
    sys.exit(main())
