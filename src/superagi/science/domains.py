from .models import ScientificDomain
def classify_domains(question: str, declared: list[str] | None = None) -> list[str]:
    result=list(declared or []); text=question.casefold()
    for term, domain in {"satellite":"Space Science","power":"Physics","quantum":"Quantum Computing","molecular":"Chemistry","chemistry":"Chemistry","robot":"Robotics","dna":"Genetics","neural":"Neuroscience"}.items():
        if term in text and domain not in result: result.append(domain)
    return result or [ScientificDomain.INTERDISCIPLINARY.value]
