# Offline EIP-712 domain check

Check that an EIP-712 request encodes the domain and primary message type you
independently intended, then optionally compare its complete digest. Python 3
standard library only; no installation, wallet, signing, network or environment
access. Copy this whole folder to use it independently.

From the repository root, run:

```sh
python3 -B line-4/tools/domain-check/domain_check.py line-4/tools/domain-check/zto-payment.json --chain-id 1 --name 'Read-only Payment Evidence' --version 1 --primary-type PaymentEvidence --no-verifier --expect 0xf33e2506e5c103f98dbfe3feb6d4b87d55f1fad4e423dbaa8462465ff4ab9774
```

Tried: exit 0, `accepted: true`, domain/type match and expected digest match.
Change `--chain-id 1` to `--chain-id 2`: exit 1, `/domain/chainId` differs,
even though the expected digest still matches. This shows why a correct hash
alone does not establish the intended chain.

The example is an unchanged copy of the ancestor encoding trace's commitment
to an observed real Ethereum ZTO transfer, transaction
`0xc4ca304c305cae326cab066639ab2156412eee7f5f774b41a2a136369f817ef7`.
It contains ZTO address `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e` and
166357571280020680094504 raw ZTO. It is a read-only evidence format, with no
verifying contract. It is **not** a ZTO permit or an authorization accepted by
a token contract. The saved example is historical; this tool does not fetch or
verify its receipt. Its example expected digest is inherited, not an independent
approval of the message.

For your request, supply trusted expectations separately from the request.
`--chain-id`, `--name`, `--version` and `--primary-type` are mandatory.
Choose exactly one of `--verifier ADDRESS` (the actual intended verifier) or
`--no-verifier` (require complete absence of that domain field). Never assume
the token address is the verifier. Use `--salt BYTES32` if the intended domain
has a salt; otherwise salt must be absent. Unknown/extra domain fields are
rejected by this deliberately narrow profile. It requires canonical standard
field types: `string`, `string`, `uint256`, `address`, `bytes32` respectively.
Other valid EIP-712 domain profiles can still be calculated with the ancestor
calculator; rejection here is a policy difference, not proof of invalid EIP-712.

`--expect DIGEST` pins all encoded message and domain data when obtained from an
independent trusted source. Without it, `matchesExpectedDigest` is `null` and
message values remain unpinned; `accepted` means only this domain/type profile
matched. The output includes the calculated digest, separator, message hash,
domain declaration order, exact differences, and whether verifier binding is
checked or explicitly absent. Domain declaration order is accepted as supplied,
as EIP-712 requires; changing it changes the separator/digest and is caught by
`--expect`. This is encoding validation, not signature recovery, replay
protection, author authentication, contract code verification, payment
acceptance or a recommendation to sign.

Exit codes: 0 matched supplied expectations; 1 well-formed request differs;
2 invalid input/expectations, unsafe path or argument error. Input files must
be regular nonhidden files beneath the current working directory. The inherited
POSIX reader uses no-follow descriptors, a 65536-byte cap, strict JSON and
bounded depth/nodes/schema. It refuses duplicate keys, floats, symlinks and
parent traversal. Incompatible platforms fail closed. Integer forms and address
case are compared by their encoded value; names/versions are exact Unicode.

Checks run:

```sh
python3 -B -m unittest discover -s line-4/tools/domain-check -v
```

All 22 tests passed: wrong/missing chain, wrong field types and widths, absent or
wrong verifier, case equivalence, salt, unknown fields, exact name/version,
primary type, reordered domains, changed message, optional digest reporting,
invalid expectations, duplicate JSON keys, immutability and CLI exit codes.
The 49 inherited digest/trace tests also passed. A detached copy reproduced the
example offline. Vendored encoder bytes are unchanged and recorded in
`provenance.json`; sharing an encoder is not independent cryptographic
verification. Domain rules follow [EIP-712](https://eips.ethereum.org/EIPS/eip-712),
particularly domain separation and acceptance of declared field order.
