from superagi.engineering import *
from superagi.engineering.circuits import *
def test_engineering_proposal_boundaries():
 m=RequirementsManager();r=m.create(statement="low power",verification_method="review");d=DesignEngine().propose("conceptual monitor",[r],[EngineeringConstraint(kind="power",limit="low")]);assert EngineeringVerifier().verify(d).status=="VERIFIED";assert MockEngineeringSimulationBackend().simulate(d).status=="SIMULATION_RESULT"
 c=Circuit(["a","b"]);c.add(CircuitComponent(identifier="R1",kind="resistor",nodes=["a","b"]));assert CircuitValidator().validate(c)["valid"]
def test_engineering_safety_and_cancel():
 p=EngineeringPipeline();p.cancel();assert p.run("conceptual",[])["status"]=="CANCELLED";assert not EngineeringSafetyPolicy().assess("real hardware command")["allowed"]
