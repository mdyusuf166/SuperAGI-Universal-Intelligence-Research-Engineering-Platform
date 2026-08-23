from ..models import QuantumAlgorithmResult
def deutsch_jozsa(is_constant): return QuantumAlgorithmResult(algorithm="Deutsch-Jozsa",output={"classification":"constant" if is_constant else "balanced"},limitations=["Reference algorithm description."])
