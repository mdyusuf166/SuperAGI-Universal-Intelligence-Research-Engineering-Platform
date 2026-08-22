from ..hypotheses.models import Hypothesis
from ..models import ResearchQuestion
from .models import ExperimentProposal, Variable, VariableClass


class ExperimentDesigner:
    def design(self, question: ResearchQuestion, hypothesis: Hypothesis) -> ExperimentProposal:
        return ExperimentProposal(objective=question.question, hypothesis=hypothesis.statement, variables=[Variable(name="panel orientation", variable_class=VariableClass.INDEPENDENT, measurement="degrees"), Variable(name="power output", variable_class=VariableClass.DEPENDENT, measurement="watts"), Variable(name="irradiance", variable_class=VariableClass.CONTROL, measurement="watts per square meter"), Variable(name="temperature", variable_class=VariableClass.CONFOUNDING, measurement="degrees Celsius")], controls=["Use the same panel and measurement interval"], procedure=["Collect repeated measurements across controlled orientations", "Hold control variables as constant as practical", "Compare output with uncertainty intervals"], measurements=["orientation", "irradiance", "temperature", "power output"], expected_outcomes=["A measurable relationship may be observed"], failure_conditions=["Insufficient variation or missing telemetry"], safety_notes=["Proposal only; do not execute physical experiments automatically"], reproducibility_notes=["Record calibration, sampling interval, units, and raw observations"])
