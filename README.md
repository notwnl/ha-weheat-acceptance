# Weheat Acceptance for Home Assistant

A separate Home Assistant custom integration for the Weheat acceptance environment.
It is generated from the official Home Assistant Core `weheat` integration and can coexist
with the official production integration.

## Base version

- Home Assistant Core: `2026.2.3`
- Custom integration domain: `weheat_acceptance`
- OAuth host: `auth.acc.weheat.nl`
- API base URL: `https://api.acc.weheat.nl/third_party`

## Generate the integration on GitHub

1. Upload this repository to an empty public GitHub repository.
2. Open **Settings > Actions > General**.
3. Under **Workflow permissions**, select **Read and write permissions**.
4. Open **Actions > Build Weheat Acceptance**.
5. Choose **Run workflow** and keep ref `2026.2.3`.
6. The workflow creates and commits `custom_components/weheat_acceptance`.
7. Create a GitHub release/tag named `2026.2.3-acc.1`.

## Install through HACS

1. HACS > Integrations > menu > Custom repositories.
2. Add this repository as type **Integration**.
3. Install **Weheat Acceptance** and restart Home Assistant.
4. Add **Weheat Acceptance** under Settings > Devices & services.
5. Enter the OAuth client ID and secret valid for the acceptance realm.

## Coexistence

The official production integration uses domain `weheat`. This integration uses
`weheat_acceptance`, so configuration entries, application credentials, devices, and entities
are registered separately.

## Security

Do not store OAuth client secrets in this repository. Enter them through Home Assistant's
Application Credentials flow.
