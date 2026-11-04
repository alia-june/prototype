"""Reference-model tests for data-touch minimization and deterministic routing."""
LEVEL={"DT0":0,"DT1":1,"DT2":2,"DT3":3,"DT4":4,"DT5":5}
ROUTES={
 "inventory":"DT1","hash":"DT2","schema":"DT3","regression":"DT3",
 "bounded_invariant":"DT4","semantic_review":"DT5"
}
checks=[]
def c(n,v): checks.append((n,bool(v)))
c("inventory-low",LEVEL[ROUTES["inventory"]] <= 1)
c("hash-no-semantic",LEVEL[ROUTES["hash"]] == 2)
c("schema-below-content",LEVEL[ROUTES["schema"]] < LEVEL["DT4"])
c("regression-below-content",LEVEL[ROUTES["regression"]] < LEVEL["DT4"])
c("probe-bounded",ROUTES["bounded_invariant"]=="DT4")
c("semantic-last",ROUTES["semantic_review"]=="DT5")
def choose(options): return min(options,key=lambda x:LEVEL[x])
c("chooser-min",choose(["DT4","DT2","DT3"])=="DT2")
def can_broaden(current,requested,authorized=False):
    return authorized and LEVEL[requested] >= LEVEL[current]
c("no-silent-broaden",not can_broaden("DT2","DT5",False))
failed=[n for n,v in checks if not v]
print(f"checks = {len(checks)}")
print(f"pass   = {len(checks)-len(failed)}")
print(f"fail   = {len(failed)}")
for n in failed: print("FAIL",n)
raise SystemExit(1 if failed else 0)
