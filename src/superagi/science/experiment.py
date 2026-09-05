from .models import ExperimentProposal
class ExperimentDesigner:
 def design(self,q,hypothesis=None): return ExperimentProposal(objective=q.question,variables=q.variables,controls=["Hold non-target variables constant."],measurements=["Declared outcome"],expected_observations=hypothesis.predicted_observations if hypothesis else [],falsification_criteria=["Observation materially differs from the proposed prediction."],risks=["NON-EXECUTING: implementation requires independent safety review."])
