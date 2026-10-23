"""What does the SCQOS Universal Transition Gateway actually refuse?"""
import sys
sys.path.insert(0, sys.argv[1])
from integration.universal_gateway import TransitionRequest, govern_transition

def run(label, **over):
    base = dict(
        tenant_id="t", external_system="DESI-DR2", subject="DESI-DR2-BAO-0",
        authority={"principal_id": "anyone", "scope": "scientific-evidence-validation"},
        intent="verify published measurements",
        evidence={"sha256": "9ac154ab"}, current_state={"value": 7.94},
        proposed_transition={"operation": "ingest"}, expected_consequence={"auditable": True},
    )
    base.update(over)
    r = govern_transition(TransitionRequest(**base))
    print(f"{r.decision:7s} {label}")

run("normal DESI-style request (as in the release)")
run("fabricated value, no evidence, intent says 'fabricate data'",
    intent="fabricate data and hide it", evidence={}, current_state={"value": -1e9})
run("principal 'nobody', scope 'whatever I want'",
    authority={"principal_id": "nobody", "scope": "whatever I want"})
run("intent 'bypass_gate' (a listed FORBIDDEN objective)", intent="bypass_gate")
run("expected_consequence says it will cause harm",
    expected_consequence={"auditable": False, "causes_harm": True})
run("scope literally 'deny'", authority={"principal_id": "x", "scope": "deny"})
