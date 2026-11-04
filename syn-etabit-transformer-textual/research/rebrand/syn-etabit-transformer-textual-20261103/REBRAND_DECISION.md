# syn-etabit-transformer-textual — Phase 1 Rebrand Decision

Date: 2026-11-03  
Authorization: AUTH-20  
Status: approved bounded prospective rebrand.

## Direct user decisions

The user directed:

> rebrand syn-etabit-transformer-textual

After receiving the concrete safe Phase 1 proposal, the user approved it with:

> yes bounded

The canonical machine-readable product brand is therefore `syn-etabit-transformer-textual`. The display name is **Syn-Etabit Transformer — Textual**.

The spelling is Etabit. The token `syn` is not expanded by this decision.

## Approved scope

The bounded rebrand covers:

1. new root `BRAND.md`;
2. current identity material in `DEVELOPMENT_PLAN.md`;
3. authorization and direct-decision records in `PROJECT_DECISIONS.md`;
4. the active product label and compatibility explanation in `service/README.md`;
5. the descriptive metadata only in `service/pyproject.toml`; and
6. this four-file rebrand record.

The new architecture statement records a forward direction:

- Markdown is the primary textual content substrate;
- JSON governs referenced document structure and emission requirements;
- resolved documents cross an Eject → Transform → Ejection boundary; and
- target-format artifacts such as DOCX are derived final emissions rather than the intermittently edited native document.

This statement does not claim that the current compatibility runtime has already migrated away from its implemented M4a adapters.

## Compatibility boundary

The following remain unchanged:

- workspace path `strmdocx`;
- Python distribution `docstream-cpu`;
- Python namespace `docstream_cpu`;
- CLI `docstream-local`;
- protocol/schema family `docstream.*`;
- state directory `.docstream`;
- database and stored receipts;
- source code and runtime behavior;
- completed pilots, inspectors, validations and manifests; and
- historical uses of Docstream and Strmdocx.

The old names are former working names and active compatibility identifiers where applicable. They are not erased or relabeled as if the new brand had existed earlier.

## Before-state identities

| File | Bytes | SHA-256 before rebrand |
| --- | ---: | --- |
| `DEVELOPMENT_PLAN.md` | 46,601 | `b58b9afb812feb15f6aee77c04152ad3f4b68c37447093d47e895c55d304e228` |
| `PROJECT_DECISIONS.md` | 39,005 | `df31932d20657ad7cb4b89711f46492baf4e500f4065021058592e308a2f6976` |
| `service/README.md` | 6,207 | `99a4f444a8486381b48e9a953b222a430a9fdaac60ea8da3564a847e668a1149` |
| `service/pyproject.toml` | 611 | `dd6f956b9b8432e72f2e743a5db5fea89cfe1abb1ad47a0b761fdf7ffc39f13b` |

Final identities and preservation checks are recorded in `VALIDATION.md` and `SOURCE_MANIFEST.json` after all approved files are finalized.

## Exclusions

This rebrand does not implement a full machine rename, external converter, namespace alias, state migration, protocol revision, release, publication, GPU path or agentic activation. Those remain behind separate production gates.
