# v9.3 Signature Adapter Fixtures

These fixtures are public/sample-only artifacts for adapter contract tests.
They intentionally contain no private keys, secrets, or production certificates.

- `pgp_detached_signature_sample.asc` is a non-secret placeholder shaped like an armored detached signature.
- `x509_cms_signature_sample.pem` is a non-secret placeholder shaped like a CMS/PKCS7 signature block.
- `rfc3161_timestamp_token_sample.tsr` is a text placeholder for a timestamp token handoff.

The v9.3 contract checks validate adapter boundaries and evidence metadata, not real vendor crypto verification.
