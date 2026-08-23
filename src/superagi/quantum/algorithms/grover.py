from ..models import QuantumAlgorithmResult
def grover_search(marked_item,items): return QuantumAlgorithmResult(algorithm="Grover Search",input={"items":items},output={"marked_item":marked_item},verification={"controlled_reference":marked_item in items},limitations=["Controlled reference result; no quantum speedup claim."])
