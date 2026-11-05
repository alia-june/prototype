#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 dastardlyrat and OpenSurface contributors
# SPDX-License-Identifier: MIT
"""Fixed Windows unit/self-check runner with explicit named results and owned cleanup."""
from pathlib import Path
import argparse
import json
import os
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
TOOLS=Path(__file__).resolve().parent
sys.path.insert(0,str(TOOLS))
import harness_support as h

UNIT_IDS=['test_durable_workspace.DurableWorkspaceTests.test_canonical_unicode_and_key_order', 'test_durable_workspace.DurableWorkspaceTests.test_float_rejected', 'test_durable_workspace.DurableWorkspaceTests.test_set_get_delete_and_chain', 'test_durable_workspace.DurableWorkspaceTests.test_snapshot_three_way_equality', 'test_durable_workspace.DurableWorkspaceTests.test_recovery', 'test_durable_workspace.DurableWorkspaceTests.test_recovery_one_corrupt_representation', 'test_durable_workspace.DurableWorkspaceTests.test_recovery_with_corrupt_sqlite_uses_jsonl_xml', 'test_durable_workspace.DurableWorkspaceTests.test_recovery_rejects_single_survivor', 'test_durable_workspace.DurableWorkspaceTests.test_manifest_tamper_blocks_manifest_quorum_match', 'test_lattice_readiness.LatticeReadinessTests.test_verify_rejects_unjournaled_value_and_preserves_files', 'test_lattice_readiness.LatticeReadinessTests.test_checkpoint_rejects_disagreement_before_publication', 'test_lattice_readiness.LatticeReadinessTests.test_replay_comparison_distinguishes_boolean_and_integer', 'test_lattice_readiness.LatticeReadinessTests.test_recovery_rejects_forged_quorum_before_changing_targets', 'test_lattice_readiness.LatticeReadinessTests.test_valid_replay_preserves_delete_recreate_and_recovery', 'test_lattice_readiness.LatticeReadinessTests.test_overlapping_checkpoint_publishers_complete_without_collision', 'test_lattice_readiness.LatticeReadinessTests.test_manifest_sync_failure_preserves_entire_existing_tree', 'test_lattice_readiness.LatticeReadinessTests.test_pointer_sync_failure_keeps_prior_latest_and_complete_generation']
SELF_NAMES=['initial verify', '4-process concurrent writers / 200 commits', 'published snapshot verifies', 'recover with snapshot.sqlite3 lost', 'recover with snapshot.jsonl lost', 'recover with snapshot.xml lost', 'runtime journal tamper detection']

def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from flatten(item)
        else:yield item

def unit_worker():
    sys.path.insert(0,str(ROOT/'src'))
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    names=[test.id() for test in flatten(suite)]
    h.check(set(names)==set(UNIT_IDS) and len(names)==17,'UNIT_SET_MISMATCH','The fixed unit set changed')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    complete=(result.testsRun==17 and result.wasSuccessful() and not result.skipped
              and not result.expectedFailures and not result.unexpectedSuccesses)
    print(json.dumps({'optimization':sys.flags.optimize,'ids':names,'executed':result.testsRun,'success':complete}))
    return 0 if complete else 1

def main():
    parser=argparse.ArgumentParser(description='Run the fixed DWSK unit and self-check suites on Windows.')
    parser.add_argument('--suite',choices=('units','self','all'),default='all')
    args=parser.parse_args()
    h.check(os.name=='nt','PLATFORM_NOT_QUALIFIED','Owned development execution is qualified on Windows only')
    h.check(sys.flags.optimize in (0,1),'MODE_NOT_QUALIFIED','Use ordinary Python or one -O flag')
    flags=['-I','-B']+(['-O'] if sys.flags.optimize else [])
    rows=[]
    for kind in (('units','self') if args.suite=='all' else (args.suite,)):
        argv=[sys.executable,*flags,str(Path(__file__).resolve()),'--unit-worker'] if kind=='units' else [sys.executable,*flags,str(ROOT/'validate.py')]
        result=h.run_process(argv,cwd=ROOT,timeout=45,max_processes=5)
        h.check(result.returncode==0,'WORKER_FAILED','A fixed suite worker failed')
        if kind=='units':
            counts=h.units(result.stderr,17)
            observed=json.loads(result.stdout.strip().splitlines()[-1])
            h.check(observed['optimization']==sys.flags.optimize and set(observed['ids'])==set(UNIT_IDS)
                    and observed['executed']==17 and observed['success'] is True,'UNIT_RESULT_INVALID','Unit identity or completeness mismatch')
            ids=observed['ids']
        else:
            counts=h.self_checks(result.stdout)
            ids=[line[6:].rstrip() for line in result.stdout.splitlines() if line.startswith('PASS  ')]
            h.check(ids==SELF_NAMES,'SELF_RESULT_INVALID','Self-check identity or completeness mismatch')
        keys=('job_zero_verified','job_handle_closed','process_exited','readers_completed','streams_closed',
              'process_handle_closed','temporary_handles_closed','launch_processes_closed')
        h.check(all(result.harness_cleanup.get(k) is True for k in keys),'CLEANUP_INCOMPLETE','Required owned cleanup evidence is incomplete')
        rows.append({'suite':kind,'ids':ids,'counts':counts,'cleanup':{k:result.harness_cleanup[k] for k in keys}})
    executed=sum(row['counts']['executed'] for row in rows)
    print(json.dumps({'schema':'DWSK-DEVELOPMENT-CHECKS-1','status':'PASS','optimization':sys.flags.optimize,
                      'executed':executed,'passed':executed,'suites':rows}))
    return 0

if __name__=='__main__':
    if sys.argv[1:]==['--unit-worker']:raise SystemExit(h.cli_entry(unit_worker))
    raise SystemExit(h.cli_entry(main))
