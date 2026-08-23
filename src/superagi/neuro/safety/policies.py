from dataclasses import dataclass
@dataclass(frozen=True)
class NeuroSafetyDecision: allowed: bool; reason: str; limitations: list[str]
def assess_neuro_request(text):
    banned=("consciousness","diagnosis","treatment","human experimentation","bci clinical")
    return NeuroSafetyDecision(False,"Unsupported neuro/medical claim.",["Computational neuroscience only."]) if any(x in text.lower() for x in banned) else NeuroSafetyDecision(True,"Computational simulation request.",["No cognition, disease, or clinical inference."])
