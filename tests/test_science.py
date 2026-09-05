from superagi.science import *
from superagi.science.domains import classify_domains
from superagi.science.discovery import cross_domain_plan
from superagi.science.equations import represent
from superagi.science.simulation import UnavailableSimulationBackend
from superagi.science import science_agent_descriptor
def test_science_pipeline_and_safety():
 q=ScientificQuestion(question="What variables influence satellite power output?",domain=["Physics","Space Science"],variables=["illumination","area","efficiency"],unknowns=["orientation"],evidence_refs=["controlled-source"]);r=SciencePipeline().run(q);assert r["hypothesis"].status=="PROPOSED" and r["simulation"].status=="SIMULATION_RESULT"
 g=CausalGraph();g.add("illumination","power");assert g.edges;assert not ScientificSafetyPolicy().assess("physical experiment in lab")["allowed"]

def test_science_typed_boundaries_and_cancellation():
 q=ScientificQuestion(question="quantum molecular chemistry",variables=["temperature"],known_facts=["A stated fact"],unknowns=["mechanism"],evidence_refs=["e1"],provenance_refs=["p1"])
 assert set(classify_domains(q.question)) >= {"Quantum Computing","Chemistry"}
 knowledge=KnowledgeSynthesizer().synthesize(q);assert knowledge["items"][0].kind == KnowledgeKind.FACT
 h=HypothesisGenerator().generate(q);assert h.status == HypothesisStatus.PROPOSED and "PROPOSED HYPOTHESIS" in h.hypothesis
 assert HypothesisCritic().critique(h)["status"] == "UNTESTED"
 g=CausalGraph();g.add("a","b","correlation");g.add("b","c","known mechanism",evidence_refs=["e1"]);assert g.paths("a") == [["a","b"]]
 assert represent("P = f(I, A)",["P","I","A"]).variables == ["P","I","A"]
 plan=cross_domain_plan(["Chemistry","Quantum Computing"],{"Chemistry":"model"},["validated backend"]);assert plan.dependencies
 unavailable=UnavailableSimulationBackend("quantum").simulate(ExperimentProposal(objective="proposal"));assert unavailable.status == "UNAVAILABLE"
 pipeline=SciencePipeline();pipeline.cancel();assert pipeline.run(q)["status"] == "CANCELLED"
 assert science_agent_descriptor().capability.domain == "science"
