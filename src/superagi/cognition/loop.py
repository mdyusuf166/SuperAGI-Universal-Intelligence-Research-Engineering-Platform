"""Bounded cognitive cycle. External actions stay unexecuted."""

from __future__ import annotations

from superagi.core.events import EventBus
from superagi.core.models import AgentResult, TaskStatus
from superagi.core.tasks import TaskManager

from .actions import ActionProposalService
from .context import CognitiveContextBuilder
from .evaluation import CognitiveEvaluator
from .learning import EvolutionProposalService, LearningProposalService
from .models import CognitiveEventName, CognitiveLifecycle, CognitiveState, CycleRequest, EpistemicStatus, FeedbackRecord, OutcomeStatus
from .perception import PerceptionLayer
from .provenance import cycle_provenance
from .reasoning import BoundedReasoner
from .routing import CognitiveRouter
from .safety import CognitiveSafetyGate
from .stages import CognitiveDecisionAdapter, CognitivePlanningAdapter, CognitivePredictionAdapter, CognitiveSimulationAdapter
from .state import CognitiveStateMachine
from .trace import CognitiveTrace


class CycleCancelled(Exception):
    """Raised between stages when cancel() was requested."""


class CognitiveCycle:
    def __init__(self, *, memory=None, graph=None, event_bus: EventBus | None = None, simulation_backend=None, tasks: TaskManager | None = None) -> None:
        self.memory = memory
        self.graph = graph
        self.bus = event_bus or EventBus()
        self.tasks = tasks or TaskManager(self.bus)
        self.simulation = CognitiveSimulationAdapter(simulation_backend)
        self.prediction = CognitivePredictionAdapter()
        self.planning = CognitivePlanningAdapter()
        self.decisions = CognitiveDecisionAdapter()
        self.actions = ActionProposalService()
        self.evaluator = CognitiveEvaluator()
        self.learning = LearningProposalService()
        self.evolution = EvolutionProposalService()
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def run(self, request: CycleRequest) -> CognitiveState:
        task = self.tasks.create_task(request.goal)
        self.tasks.update_task(task.id, TaskStatus.QUEUED)
        self.tasks.update_task(task.id, TaskStatus.RUNNING)
        machine = CognitiveStateMachine()
        trace = CognitiveTrace(self.bus, task.id)
        state = CognitiveState(task_id=task.id, goal=request.goal, provenance=cycle_provenance(request.source, task_id=str(task.id), cycle_id="pending"))
        state.provenance = cycle_provenance(request.source, task_id=str(task.id), cycle_id=str(state.cycle_id))
        trace.add(CognitiveEventName.CYCLE_STARTED, "Cognitive cycle started.")
        try:
            if self._stopped(state, machine, trace, task):
                return state
            safety = CognitiveSafetyGate().review(" ".join([request.goal, *[item.statement for item in request.observations]]))
            state.safety_status = safety
            trace.add(CognitiveEventName.SAFETY_REVIEWED, "allowed" if safety.allowed else "rejected")
            if not safety.allowed:
                return self._fail(state, machine, trace, task, "Safety policy rejected the cycle")
            self._advance(machine, CognitiveLifecycle.INGESTING)
            ingested = PerceptionLayer().ingest(request.observations, source=request.source)
            state.observations = list(ingested.observations)
            state.evidence_refs = [ref for item in state.observations for ref in item.evidence_refs]
            trace.add(CognitiveEventName.OBSERVATION_INGESTED, f"Ingested {len(state.observations)} observations.")
            if self._stopped(state, machine, trace, task):
                return state
            domain = CognitiveRouter().route(request.goal, request.domains)
            state.domain_result = domain
            personal = request.goal if any(item.domain == "personal" for item in domain.contributions) else None
            if personal:
                from superagi.personal.services import GoalManager

                personal = GoalManager().create(personal[:120]).title
            research_notes = list(request.research_notes)
            research_note = None
            if request.question:
                from superagi.science.hypothesis import HypothesisGenerator
                from superagi.science.models import ScientificQuestion

                hypothesis = HypothesisGenerator().generate(ScientificQuestion(question=request.question, evidence_refs=[request.source] if request.source else [], assumptions=list(request.assumptions)))
                research_note = hypothesis.hypothesis
                research_notes.append(research_note)
            context = CognitiveContextBuilder().build(goal=request.goal, observations=state.observations, memory=self.memory, graph=self.graph, constraints=request.constraints, research_notes=research_notes, source=request.source, personal_goal=personal)
            state.context = context
            state.memory_refs = [item.ref_id for item in context.memories if item.ref_id]
            state.world_model_refs = [item.ref_id for item in context.entities + context.relations if item.ref_id]
            self._advance(machine, CognitiveLifecycle.CONTEXT_READY)
            trace.add(CognitiveEventName.CONTEXT_BUILT, f"Bounded context memories={len(context.memories)} entities={len(context.entities)}.")
            self._advance(machine, CognitiveLifecycle.REASONING)
            state.reasoning_result = BoundedReasoner().reason(goal=request.goal, context=context, assumptions=list(request.assumptions), research_note=research_note)
            trace.add(CognitiveEventName.REASONING_COMPLETED, f"Claims {len(state.reasoning_result.claims)}; inferences {len(state.reasoning_result.inferences)}.")
            if request.simulate:
                self._advance(machine, CognitiveLifecycle.SIMULATING)
                state.simulation_result = self.simulation.run(signals=request.signals, deltas=request.deltas)
                trace.add(CognitiveEventName.SIMULATION_COMPLETED, state.simulation_result.status)
            if request.predict:
                self._advance(machine, CognitiveLifecycle.PREDICTING)
                state.prediction_result = self.prediction.project(request.series)
                trace.add(CognitiveEventName.PREDICTION_COMPLETED, state.prediction_result.epistemic.value)
            self._advance(machine, CognitiveLifecycle.PLANNING)
            state.plan_result = self.planning.propose(goal=request.goal, signals=request.signals, constraints=request.constraints)
            trace.add(CognitiveEventName.PLAN_CREATED, "Plan proposal. executed is false.")
            self._advance(machine, CognitiveLifecycle.DECISION_REVIEW)
            evidence = state.evidence_refs or ([request.source] if request.source else [])
            state.decision_result = self.decisions.prepare(question=request.goal, options=[item.domain for item in domain.contributions] or ["review"], criteria=["risk"], evidence=evidence, assumptions=list(request.assumptions) or ["The cycle does not execute the proposal."], risks=["Mock or unavailable results are not physical outcomes."], human_approved=bool(request.human_approved and request.approval_required))
            trace.add(CognitiveEventName.DECISION_PROPOSED, state.decision_result.status)
            self._advance(machine, CognitiveLifecycle.ACTION_PROPOSED)
            proposal = self.actions.create(action="review-context", reason="Bounded proposal from the cognitive cycle.", evidence=evidence, risk="low", constraints=request.constraints, approval_required=request.approval_required, approved=request.human_approved, source=request.source)
            state.action_proposals = [proposal]
            trace.add(CognitiveEventName.ACTION_PROPOSED, proposal.approval_status.value)
            if request.approval_required and not request.human_approved:
                state.feedback = FeedbackRecord(status=OutcomeStatus.NOT_EXECUTED, statement=request.outcome_statement or "Approval was not granted.", synthetic=True, limitations=["NOT_EXECUTED. A supplied success label cannot replace approval."])
                trace.add(CognitiveEventName.APPROVAL_REQUIRED, "Human approval is required. The proposal was not executed.")
                state.evaluation = self.evaluator.evaluate(state)
                state.learning_update = self.learning.propose(state)
                state.evolution_proposal = self.evolution.propose(state.learning_update, source=request.source)
                trace.add(CognitiveEventName.LEARNING_PROPOSED, state.learning_update.gap)
                trace.add(CognitiveEventName.EVOLUTION_PROPOSED, state.evolution_proposal.lifecycle)
                self._advance(machine, CognitiveLifecycle.AWAITING_HUMAN_APPROVAL)
                return self._finish(state, machine, trace, task, complete_task=False)
            self._advance(machine, CognitiveLifecycle.OBSERVING)
            outcome = request.outcome or OutcomeStatus.UNKNOWN_OUTCOME
            state.feedback = FeedbackRecord(status=outcome, statement=request.outcome_statement or "Caller-supplied synthetic observation.", synthetic=True, limitations=["This observation was supplied by the caller. It is not a measured real-world outcome."])
            trace.add(CognitiveEventName.OBSERVATION_RECEIVED, outcome.value)
            self._advance(machine, CognitiveLifecycle.EVALUATING)
            state.evaluation = self.evaluator.evaluate(state)
            trace.add(CognitiveEventName.EVALUATION_COMPLETED, "Structural evaluation. Accuracy was not invented.")
            self._advance(machine, CognitiveLifecycle.LEARNING)
            state.learning_update = self.learning.propose(state)
            trace.add(CognitiveEventName.LEARNING_PROPOSED, state.learning_update.gap)
            self._advance(machine, CognitiveLifecycle.EVOLUTION_REVIEW)
            state.evolution_proposal = self.evolution.propose(state.learning_update, source=request.source)
            trace.add(CognitiveEventName.EVOLUTION_PROPOSED, state.evolution_proposal.lifecycle)
            self._remember(state, request)
            self._annotate(state)
            self._advance(machine, CognitiveLifecycle.COMPLETED)
            trace.add(CognitiveEventName.CYCLE_COMPLETED, "Proposal cycle completed. executed is false.")
            return self._finish(state, machine, trace, task, complete_task=True)
        except CycleCancelled:
            return self._stopped(state, machine, trace, task)
        except ValueError as exc:
            return self._fail(state, machine, trace, task, str(exc))

    def _advance(self, machine: CognitiveStateMachine, target: CognitiveLifecycle) -> None:
        if self._cancel:
            raise CycleCancelled()
        machine.move(target)

    def _stopped(self, state, machine, trace, task) -> bool:
        if not self._cancel:
            return False
        if machine.state not in {CognitiveLifecycle.COMPLETED, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED}:
            machine.cancel()
        trace.add(CognitiveEventName.CYCLE_FAILED, "Cycle cancelled.")
        self.tasks.cancel_task(task.id)
        self._sync(state, machine, trace)
        state.failure = "cancelled"
        state.executed = False
        return True

    def _fail(self, state, machine, trace, task, reason: str) -> CognitiveState:
        if machine.state not in {CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED, CognitiveLifecycle.COMPLETED, CognitiveLifecycle.AWAITING_HUMAN_APPROVAL}:
            machine.fail()
        trace.add(CognitiveEventName.CYCLE_FAILED, reason)
        if task.status == TaskStatus.RUNNING:
            self.tasks.update_task(task.id, TaskStatus.FAILED, error=reason)
        self._sync(state, machine, trace)
        state.failure = reason
        state.executed = False
        state.limitations = ["The cycle stopped on a failed dependency."]
        return state

    def _finish(self, state, machine, trace, task, *, complete_task: bool) -> CognitiveState:
        self._sync(state, machine, trace)
        state.executed = False
        state.limitations = ["SIMULATION ONLY where a mock backend ran.", "PROPOSAL ONLY.", "NO REAL-WORLD EXECUTION."]
        if complete_task and task.status == TaskStatus.RUNNING:
            self.tasks.update_task(task.id, TaskStatus.COMPLETED, result=AgentResult(success=True, output={"executed": False, "lifecycle": state.lifecycle.value}, summary="Cognitive proposal cycle.", limitations=state.limitations))
        return state

    def _sync(self, state, machine, trace) -> None:
        state.lifecycle = machine.state
        state.history = list(machine.history)
        state.events = list(trace.records)

    def _remember(self, state: CognitiveState, request: CycleRequest) -> None:
        if self.memory is None or not request.source:
            return
        self.memory.remember(f"Cognitive cycle proposal: {request.goal}", source=request.source, tags=("cognition",))

    def _annotate(self, state: CognitiveState) -> None:
        if self.graph is None or state.prediction_result is None or state.prediction_result.epistemic != EpistemicStatus.PREDICTED or not state.prediction_result.values:
            return
        entities = self.graph.entities()
        if not entities:
            return
        from superagi.world_model.models import EntityProperty, EpistemicStatus as WorldEpistemic, EvidenceLinkStatus, PropertyValue
        from superagi.world_model.provenance import provenance_from

        self.graph.add_annotation(entities[0].id, EntityProperty(name="cognitive_prediction", value=PropertyValue(number=state.prediction_result.values[0]), epistemic=WorldEpistemic.PREDICTED, status=EvidenceLinkStatus.UNKNOWN, provenance=provenance_from(state.provenance.prediction.source, agent="cognitive_cycle")))
