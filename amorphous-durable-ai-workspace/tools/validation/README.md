# DWSK development validation

This source-only Windows tool runs the fixed 17 unit tests and seven self-checks through the repaired owned-process wrapper. It accepts no arbitrary command or executable argument. It is not part of the runtime library API and is not installed as a console command.

From the project source directory:

```powershell
python -I -B tools/validation/run_checks.py --suite all
python -I -B -O tools/validation/run_checks.py --suite all
```

Use `--suite units` or `--suite self` for one fixed suite. Normal and optimized results identify their actual mode and exact named tests. Success requires expected counts, no skipped unit tests and explicit process/job/stream/handle cleanup. Worker timeout or cleanup uncertainty is incomplete and has a nonzero exit. The self-check uses four writer children; the helper owns only the processes it launches.

The full R4 recovery/value/fault qualification is a separate development campaign whose bounded summary appears in the project validation report. Running these 24 cases does not reproduce that complete campaign. Marker protocols do not constrain external tools, and neither this runner nor process interruption proves physical power-loss safety. Keep raw diagnostics private; errors can include environment paths. No extra runtime dependency is introduced.
