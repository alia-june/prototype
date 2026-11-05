`[GENERATED-PROMPT]`

## Copy-first and version-lineage control

### Effect

Copy-first work prevents an admitted original from becoming the transformation surface. Version lineage supports comparison, audit, rejection, rollback, and recovery. A copy can reproduce existing corruption; duplication alone is not validation.

### Rules

1. Never modify the admitted original in place.
2. Record original identity, location, provenance, size, checksum or verification state, and write-protection state when available.
3. Create and verify a working copy before transformation.
4. Create a new child version for every material transformation.
5. Preserve the parent until validation, explicit promotion or rejection, and recovery disposition are complete.
6. Promotion requires explicit authorization and changes operational selection, not historical provenance.
7. A rejected version remains in the lineage record.
8. A same-device copy is not an independent recovery copy.
9. Retention is not recovery until restoration is tested.
10. Halt before material mutation if no recoverable pre-change state exists.

### Version record

```text
VERSION ID:
PARENT ID:
ORIGINAL SOURCE ID:
SOURCE CHECKSUM / VERIFICATION:
RESULT CHECKSUM / VERIFICATION:
TRANSFORMATION:
ACTOR:
AUTHORITY SOURCE:
TOOL OR PROCESS:
VALIDATION RESULT:
ACCEPTANCE STATUS:
PROMOTION STATUS:
RECOVERY LOCATION:
RECOVERY PROCEDURE:
RESTORATION TEST STATUS:
RETENTION RULE: ${RETENTION_RULE}
```
