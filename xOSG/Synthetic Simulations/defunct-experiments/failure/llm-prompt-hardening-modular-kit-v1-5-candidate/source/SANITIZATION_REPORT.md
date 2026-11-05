# Sanitization Report

## Decision

Prepared and admitted as a private-repository publication under MIT. Repository visibility remains private.

## Preserved

- assembler and configuration;
- 17 prompt modules;
- 12 templates;
- 5 heuristics;
- behavioral vectors and 34 substantive historical regression tests;
- generated historical audits;
- exact digest receipts for 16 omitted parent, source, and vendor members.

## Removed from the publication surface

- 4 recursive parent ZIPs;
- 1 historical parent prompt payload;
- 9 source and source-record payloads, including the DOCX;
- 1 vendor ZIP and its generated source record;
- 12 generated builds;
- vendor bytecode, run logs, caches, and nested historical material contained inside the omitted vendor archive.

## Changes required by sanitation

- replaced the original package README, provenance, and validation text with publication-scoped records;
- changed the external-engine preflight to use the consolidated receipt instead of an absent vendor path;
- removed tests that required omitted payload bytes or checked-in generated builds;
- added two publication-surface tests;
- retained the known Windows mode-preservation failure unchanged.

## Scan result

The staged tree contains only Markdown, JSON, and Python source. The bounded residue scan found no private Windows or Linux home paths, user identifier, email address, API-key assignment, archive, DOCX, bytecode, or log file.

## License resolution

The project-owned sanitized source is licensed under MIT by explicit user authorization dated 2026-11-01. The optional vendor engine remains separately MIT-licensed by m.A.R.S. and is not included.

