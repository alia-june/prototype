# Theory inspector contract

The `docstream_cpu.theory_inspector` package is a read-only AUTH-18B packet inspector. Import performs no I/O. Construction requires a root containing `inspection_index.json`.

## Trust boundary

The loader requires the exact index schema, root-contained `.json` paths, declared byte sizes, SHA-256 hashes, declared document schemas and record counts. JSON duplicate keys, duplicate record IDs, missing cross-catalog links and the fields `command`, `executable`, `script`, `eval`, `shell` or `plugin` are rejected with stable codes.

Default ceilings are 2 MiB per file, 10 MiB total, 1,000 records, 1,000 query results, trace depth 16 and 128 trace links. The loaded view is detached from parsed input and exposes no mutation or persistence operation.

## Commands

Run with:

```text
python -m docstream_cpu.theory_inspector --root <study-root> [--format text|json] <command>
```

Commands are `summary`, `sources`, `source`, `relations`, `relation`, `crosswalk`, `crosswalk-entry`, `trace`, `gaps`, `conflicts`, `sample` and `validate`. Plural commands accept text, status, domain, source and limit filters as applicable. Singular commands retrieve a globally unique record ID. `trace` follows only explicit catalog references; external AUTH-18A source-record hashes are data, not catalog links.

The browser dashboard is a separate static view. It uses no network requests, interprets no executable data and renders catalog content with text nodes.
