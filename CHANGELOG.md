# Changelog

All relevant changes to this project should be recorded here.

The format follows this convention:

- `feat:` new features
- `fix:` bug fixes
- `refactor:` internal refactoring
- `docs:` documentation
- `test:` tests

## [Unreleased]

- No pending entries.

## [0.2.3] - 2026-04-10

- `docs:` updated the published README badge and release highlight so the PyPI page for `0.2.3` points to tag `v0.2.3`

## [0.2.2] - 2026-04-10

- `docs:` updated the README release badge and release highlight to point to `v0.2.1` before republishing on PyPI

## [0.2.1] - 2026-04-10

- `fix:` fallback field-type resolution in the high-level card update flow now consults the full pipe schema when the field is not present in the current phase or card payload
- `test:` added unit coverage for updating start form fields that are absent from the loaded card fields

## [0.2.0] - 2026-04-10

- `feat:` added `TransportConfig` as a public transport-layer configuration object
- `feat:` added TLS/SSL controls with `verify_ssl` and `ca_bundle_path`
- `feat:` added conservative transport retry for timeout and connection failures
- `feat:` expanded pipe field catalog coverage with `start_form_fields` and `internal_id`
- `feat:` added safe card creation through `api.cards.createSafely(...)`
- `fix:` corrected `createCard` mutation serialization to use valid GraphQL input for `fields_attributes`
- `fix:` ensured service-level operations honor transport timeout overrides
- `fix:` aligned `createSafely(...)` option validation with `InvalidFieldOptionError`
- `docs:` updated README and examples to document start form semantics and connector record id behavior
- `docs:` documented the destructive live integration battery that creates one card, mutates only that card, and can clean it up safely
- `test:` added unit coverage for transport configuration, retry behavior, create mutation serialization, and safe start form creation
- `test:` hardened the live integration battery to propagate one created card through create, update, move, destination update, and optional delete
