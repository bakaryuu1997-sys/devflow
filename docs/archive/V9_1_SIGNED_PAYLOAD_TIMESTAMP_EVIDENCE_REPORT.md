# v9.1 Signed Payload Import + Timestamp Token Evidence Report

## Scope

v9.1 adds the missing evidence loop after v9.0 external signing handoff.

## Added

- Signed payload import package endpoint.
- Signed payload verification record endpoint.
- Timestamp token evidence package endpoint.
- Timestamp token evidence attachment endpoint.
- Combined signed payload + timestamp integrity check.
- CLI exports for signed payload import and timestamp token evidence package.

## Safety stance

The app still does not store private keys and does not perform legal cryptographic signing internally. It stores payload hashes, signature hashes/references, timestamp token hashes/references, and verification status.

## Result

The governance workflow can now prove that an external signature and timestamp token were attached to the same canonical evidence payload.
