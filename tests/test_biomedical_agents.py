import asyncio
from superagi.biomedical.agents import DNAAgent, MolecularAgent
from superagi.core.models import AgentContext, Task

def test_agents_return_structured_results():
    task = Task(description="ATGC")
    dna = asyncio.run(DNAAgent().run(task, AgentContext(task_id=task.id, values={"sequence": "ATGC", "motif": "TG"})))
    assert dna.success and dna.output["classification"] == "COMPUTATIONAL_RESULT"
    molecular = asyncio.run(MolecularAgent().run(Task(description="CCO"), AgentContext(task_id=task.id, values={"smiles": "CCO"})))
    assert molecular.output["classification"] == "COMPUTATIONAL_RESULT"
