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
  controller=SystemComponent(name="conceptual-controller",kind="controller");sensor=SystemComponent(name="conceptual-sensor",kind="sensor");interface=SystemInterface(name="sensor-to-controller",source="conceptual-sensor",target="conceptual-controller",protocol="conceptual",compatible=True);arch=SystemArchitecture(name="conceptual-system",subsystems=[Subsystem(name="core",components=[controller,sensor])],interfaces=[interface]);decisions=["Conceptual architecture proposed."]
  if any(getattr(item,"kind",None)=="power" for item in constraints): decisions.append("Power consideration: conceptual low-power budget; not a measured electrical design.")
  return EngineeringDesign(problem=problem,requirements=list(requirements),architecture=arch,components=[controller,sensor],interfaces=[interface],constraints=list(constraints),decisions=decisions,provenance=["engineering-pipeline"])
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
 _BLOCKED=("real hardware","physical engineering","dangerous operation","firmware flash","physical hardware","destructive operation","unsafe actuator","dangerous electrical","laboratory execution","unsafe laboratory","autonomous physical deployment")
 def assess(self,text):
  folded=text.casefold();hit=[x for x in self._BLOCKED if x in folded];return {"allowed":not hit,"mode":"DESIGN_SIMULATION_ONLY","reasons":hit}
class DesignReview:
 def review(self,design,simulation=None,risks=None):
  findings=[]
  for requirement in design.requirements:
   if not requirement.statement or not requirement.verification_method: findings.append(ReviewFinding(category="missing_requirements",message=f"Requirement is incomplete: {requirement.statement!r}",severity=ReviewSeverity.ERROR))
   elif not requirement.measurable: findings.append(ReviewFinding(category="missing_requirements",message=f"Requirement is not measurable: {requirement.statement}",severity=ReviewSeverity.WARNING))
  blob=" ".join([*design.decisions,*design.assumptions]).casefold()
  for constraint in design.constraints:
   if not constraint.limit or f"violates:{constraint.kind}".casefold() in blob: findings.append(ReviewFinding(category="violated_constraints",message=f"Constraint {constraint.kind} is violated or unbounded.",severity=ReviewSeverity.ERROR))
  for interface in design.interfaces:
   if not interface.compatible: findings.append(ReviewFinding(category="interface_incompatibilities",message=f"Interface {interface.name} is incompatible.",severity=ReviewSeverity.ERROR))
  for assumption in design.assumptions:
   if "unsupported" in assumption.casefold(): findings.append(ReviewFinding(category="unsupported_assumptions",message=assumption,severity=ReviewSeverity.ERROR))
  if not design.provenance: findings.append(ReviewFinding(category="missing_provenance",message="Missing provenance.",severity=ReviewSeverity.ERROR))
  if simulation is not None and getattr(simulation,"status",None) in {"UNAVAILABLE","SIMULATION_BACKEND_UNAVAILABLE"}: findings.append(ReviewFinding(category="unavailable_simulation",message="SIMULATION_BACKEND_UNAVAILABLE",severity=ReviewSeverity.WARNING))
  for risk in risks or []:
   severity=ReviewSeverity.CRITICAL if "critical" in risk.casefold() else ReviewSeverity.WARNING
   findings.append(ReviewFinding(category="unresolved_risks",message=risk,severity=severity))
  if not EngineeringSafetyPolicy().assess(design.problem)["allowed"]: findings.append(ReviewFinding(category="unresolved_risks",message="Safety policy rejected the design problem.",severity=ReviewSeverity.CRITICAL))
  severities={item.severity for item in findings}
  if ReviewSeverity.CRITICAL in severities: status,accepted="REJECTED",False
  elif ReviewSeverity.ERROR in severities: status,accepted="PARTIALLY_VERIFIED",False
  elif findings: status,accepted="PARTIALLY_VERIFIED",True
  else: status,accepted="VERIFIED",True
  return DesignReviewReport(issues=[f"{item.severity}: {item.category}: {item.message}" for item in findings],status=status,findings=findings,accepted=accepted)
