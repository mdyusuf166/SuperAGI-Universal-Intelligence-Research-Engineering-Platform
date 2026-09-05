from .models import *
class RequirementsManager:
 def __init__(self):self.items=[];self.traces={}
 def create(self,**kw): r=EngineeringRequirement(**kw);self.items.append(r);return r
 def update(self,id,**kw): r=next(x for x in self.items if x.id==id);[setattr(r,k,v) for k,v in kw.items()];return r
 def validate(self):return all(x.statement and x.verification_method for x in self.items)
 def trace(self,requirement,decision):self.traces[str(requirement.id)]=decision
 def prioritize(self):return sorted(self.items,key=lambda x:x.priority)
class DesignEngine:
 def propose(self,problem,requirements,constraints=()):
  component=SystemComponent(name="conceptual-controller",kind="controller");arch=SystemArchitecture(name="conceptual-system",subsystems=[Subsystem(name="core",components=[component])]);return EngineeringDesign(problem=problem,requirements=list(requirements),architecture=arch,components=[component],constraints=list(constraints),decisions=["Conceptual architecture proposed."],provenance=["engineering-pipeline"])
 def missing_requirements(self,design):return [r.statement for r in design.requirements if not r.measurable]
 def incompatible(self,design):return [i.name for i in design.interfaces if not i.compatible]
class EngineeringSimulationBackend:
 name="backend";available=False
 def simulate(self,design):return EngineeringSimulationResult(backend=self.name,status="UNAVAILABLE",limitations=["No verified computational backend available; no mock substituted."])
class MockEngineeringSimulationBackend(EngineeringSimulationBackend):
 name="mock";available=True
 def simulate(self,design):return EngineeringSimulationResult(backend=self.name,status="SIMULATION_RESULT",output={"components":len(design.components)},limitations=["Deterministic test mock only; not real hardware validation."])
class EngineeringVerifier:
 def verify(self,design):
  checks={"requirements_coverage":bool(design.requirements),"constraint_coverage":bool(design.constraints),"architecture_consistency":bool(design.architecture.subsystems),"interface_consistency":all(i.compatible for i in design.interfaces),"component_compatibility":not DesignEngine().incompatible(design),"provenance":bool(design.provenance)};return VerificationResult(status="VERIFIED" if all(checks.values()) else "PARTIALLY_VERIFIED",checks=checks,limitations=["Not physical certification."])
class TradeoffAnalyzer:
 def compare(self,alternatives):
  scores={name:sum(values.values()) for name,values in alternatives.items()};best=min(scores,key=scores.get);return TradeoffAnalysis(criteria=scores,recommendation=best,reason="Lowest explicit aggregate criterion score.")
class EngineeringOptimizer:
 def minimize(self,candidates,target=0): return min(candidates,key=lambda x:(x.get("cost",0)+x.get("power",0),-x.get("performance",0)))
class EngineeringSafetyPolicy:
 def assess(self,text):
  hit=[x for x in ("real hardware","physical engineering","dangerous operation","firmware flash") if x in text.casefold()];return {"allowed":not hit,"mode":"DESIGN_SIMULATION_ONLY","reasons":hit}
class DesignReview:
 def review(self,design):
  issues=DesignEngine().missing_requirements(design)+DesignEngine().incompatible(design)+([] if design.provenance else ["Missing provenance."]);return DesignReviewReport(issues=issues,status="VERIFIED" if not issues else "PARTIALLY_VERIFIED")
