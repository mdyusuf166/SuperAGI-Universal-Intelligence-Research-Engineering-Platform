from superagi.science import *
from superagi.science.discovery import cross_domain_plan

satellite = ScientificQuestion(question="What variables influence satellite power output?", domain=["Physics", "Space Science"], variables=["illumination", "area", "efficiency", "orientation"], known_facts=["Power depends on available energy conversion."], unknowns=["orbital shading"], evidence_refs=["synthetic-demo-source"], provenance_refs=["demo-provenance"])
print("SATELLITE PROPOSAL (not a discovery)")
print(SciencePipeline().run(satellite))

conceptual = ScientificQuestion(question="Can quantum computing concepts and molecular modeling be combined to investigate a chemistry research problem?", domain=["Quantum Computing", "Chemistry"], unknowns=["Suitable validated computational method"], constraints=["Conceptual/computational demonstration only"])
plan = cross_domain_plan(conceptual.domain, {"Quantum Computing": "Algorithm concepts", "Chemistry": "Molecular-model representation"}, ["Validated simulator required before scientific use"])
print("\nINTERDISCIPLINARY CONCEPTUAL PROPOSAL (no laboratory claim)")
print({"pipeline": SciencePipeline().run(conceptual), "cross_domain_plan": plan})
