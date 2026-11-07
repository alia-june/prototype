# How to inspect a Code-Lexigraph reconstruction

Use the retained safe fall-through example to follow one declared requirement into generated Python and back to its source records. This guide constructs and inspects the output without executing the generated program.

Run the commands in PowerShell from `code-lexigraph/`, with Python available. The recorded repository replay used Python 3.14.3. The example writes to a fresh temporary directory rather than the source tree.

## Construct the example

```powershell
$ErrorActionPreference = 'Stop'
$reviewDir = Join-Path ([IO.Path]::GetTempPath()) ('code-lexigraph-review-' + [guid]::NewGuid().ToString('N'))
python -B -m code_lexigraph examples/safe_fallthrough.bundle.json --out $reviewDir
if ($LASTEXITCODE -ne 0) { throw 'Construction failed.' }
Get-ChildItem -LiteralPath $reviewDir -Name
```

Expect `example.py`, `CONTRACT.md`, and `TRACE.json`. The CLI refuses to overwrite existing outputs with those names. Use a fresh output directory for another construction.

## Follow the requirement into the code

1. Open `CONTRACT.md`. The survivor is the exact caller-supplied `required_json` text. The operation receives a separately parsed working representation. The surrounding system owns the exception response.
2. Open `example.py`. Locate the `ERROR` gate and the separate path for an exception after invocation. The first blocks decoding and invocation; the second reports an exception while retaining the declared survivor. These are different cases in this construction profile.
3. Open `TRACE.json` and inspect a declared link:

```powershell
$mapping = Get-Content -LiteralPath (Join-Path $reviewDir 'TRACE.json') -Raw | ConvertFrom-Json
$link = $mapping.trace | Where-Object { $_.blueprint -eq 'B03' }
$link | ConvertTo-Json -Depth 5
$mapping.inverse.C01
```

For this bundle, `B03` maps to code record `C01`, meaning records `D07`, `P04`, `P05`, and `L01`, and generated lines 5–9. Looking up `C01` in `inverse` returns `B03` and `B01`. The separate `spans` map locates blueprint records in the generated text. Use the [input bundle](examples/safe_fallthrough.bundle.json) to inspect the referenced records rather than guessing what an identifier means.

The output directory is retained for inspection. A trace connects the declared records and generated locations; it does not prove every possible input, operation, or surrounding exception policy is correct. See the [design guide](docs/DESIGN.md) for the construction boundary and the [validation record](docs/VALIDATION.md) for the cases actually tested. The [README](README.md#replay-the-checks) gives the full regression command.
