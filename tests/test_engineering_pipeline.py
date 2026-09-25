from superagi.engineering import *
def test_pipeline():
 r=EngineeringRequirement(statement="measure",verification_method="simulation")
 assert EngineeringPipeline().run("conceptual monitoring system",[r],[EngineeringConstraint(kind="power",limit="low")])["status"]=="COMPLETED"
