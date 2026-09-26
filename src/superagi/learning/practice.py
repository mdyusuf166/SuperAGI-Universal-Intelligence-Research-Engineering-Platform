"""Deterministic and simulated practice. Scores exist only when computable."""

from __future__ import annotations

from collections.abc import Callable

from superagi.evolution.models import SimulationAction, SimulationScenario, SimulationState, StateVariable, TerminationCondition
from superagi.evolution.simulation import MockSimulationBackend

from .models import ExperienceKind, PracticeAttempt, PracticeMode, PracticeTask, SkillEvidence
from .provenance import provenance
from .safety import LearningSafetyPolicy

SIMULATED_LIMITS = ["SIMULATED_PRACTICE is not real-world competence.", "Mock deterministic backend."]
PRACTICE_LIMITS = ["Practice is not mastery.", "One attempt is not a general skill."]


class PracticeEngine:
    def __init__(self) -> None:
        self.safety = LearningSafetyPolicy()

    def problem(self, task: PracticeTask, answer: str, *, source: str | None = None) -> PracticeAttempt:
        self.safety.guard(f"{task.prompt} {answer}")
        if task.expected is None:
            return PracticeAttempt(task_id=task.id, skill=task.skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=answer, result="No expected answer was supplied.", passed=None, feedback="Cannot evaluate without an expected answer.", score_status="NOT_EVALUABLE", provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS)
        passed = answer.strip().casefold() == task.expected.strip().casefold()
        evidence = [SkillEvidence(skill=task.skill, statement=f"{task.kind} practice {'matched' if passed else 'did not match'} the expected answer.", kind=ExperienceKind.SYNTHETIC, passed=passed, provenance=provenance(source, agent="practice_engine"))]
        return PracticeAttempt(task_id=task.id, skill=task.skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=answer, result="match" if passed else "mismatch", passed=passed, errors=[] if passed else [f"expected {task.expected}"], feedback="Correct against the supplied answer." if passed else "Compare with the supplied answer.", score=1.0 if passed else 0.0, score_status="COMPUTED", evidence=evidence, provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS)

    def code(self, skill: str, function: Callable, cases: list[tuple[tuple, object]], *, source: str | None = None) -> PracticeAttempt:
        task = PracticeTask(skill=skill, prompt=getattr(function, "__name__", "function"), kind="code")
        if not cases:
            return PracticeAttempt(task_id=task.id, skill=skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=task.prompt, result="No test cases were supplied.", score_status="NOT_EVALUABLE", provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS)
        errors = []
        for arguments, expected in cases:
            try:
                actual = function(*arguments)
            except Exception as exc:
                errors.append(f"{arguments}: raised {type(exc).__name__}")
                continue
            if actual != expected:
                errors.append(f"{arguments}: expected {expected!r}, got {actual!r}")
        passed = not errors
        score = (len(cases) - len(errors)) / len(cases)
        evidence = [SkillEvidence(skill=skill, statement=f"{len(cases) - len(errors)}/{len(cases)} supplied test cases passed.", kind=ExperienceKind.SYNTHETIC, passed=passed, provenance=provenance(source, agent="practice_engine"))]
        return PracticeAttempt(task_id=task.id, skill=skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=task.prompt, result="all tests passed" if passed else "some tests failed", passed=passed, errors=errors, feedback="Supplied tests pass." if passed else "Fix the failing cases.", score=score, score_status="COMPUTED", evidence=evidence, provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS + ["Passing supplied tests is not proof of correctness."])

    def research(self, skill: str, claim: str, cited: list[str], required: list[str], *, source: str | None = None) -> PracticeAttempt:
        self.safety.guard(claim)
        task = PracticeTask(skill=skill, prompt=claim, kind="research")
        if not required:
            return PracticeAttempt(task_id=task.id, skill=skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=claim, result="No evidence requirement was supplied.", score_status="NOT_EVALUABLE", provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS)
        missing = [item for item in required if item not in cited]
        passed = not missing
        coverage = (len(required) - len(missing)) / len(required)
        evidence = [SkillEvidence(skill=skill, statement=f"Evidence coverage {len(required) - len(missing)}/{len(required)}.", kind=ExperienceKind.SYNTHETIC, passed=passed, provenance=provenance(source, agent="practice_engine"))]
        return PracticeAttempt(task_id=task.id, skill=skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=claim, result="evidence complete" if passed else "evidence incomplete", passed=passed, errors=[f"missing evidence: {item}" for item in missing], feedback="All required evidence is cited." if passed else "Cite the missing evidence.", score=coverage, score_status="COMPUTED", evidence=evidence, provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS + ["Citation coverage is not scientific validity."])

    def hypothesis(self, skill: str, prediction: float, observed: float | None, tolerance: float, *, source: str | None = None) -> PracticeAttempt:
        task = PracticeTask(skill=skill, prompt=f"predict {prediction}", kind="hypothesis")
        if observed is None:
            return PracticeAttempt(task_id=task.id, skill=skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=task.prompt, result="No observation was supplied.", score_status="NOT_EVALUABLE", provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS + ["Prediction is not knowledge."])
        error = abs(prediction - observed)
        passed = error <= tolerance
        evidence = [SkillEvidence(skill=skill, statement=f"Absolute error {error} against a supplied observation.", kind=ExperienceKind.SYNTHETIC, passed=passed, provenance=provenance(source, agent="practice_engine"))]
        return PracticeAttempt(task_id=task.id, skill=skill, mode=PracticeMode.DETERMINISTIC_PRACTICE, attempt=task.prompt, result=f"absolute error {error}", passed=passed, errors=[] if passed else [f"error {error} exceeds tolerance {tolerance}"], feedback="Within tolerance." if passed else "Outside tolerance.", score=error, score_status="COMPUTED_ABSOLUTE_ERROR", evidence=evidence, provenance=provenance(source, agent="practice_engine"), limitations=PRACTICE_LIMITS + ["Prediction is not knowledge."])

    def simulate(self, skill: str, initial: dict[str, float], steps: list[dict[str, float]], *, target: dict[str, float] | None = None, bounds: dict[str, tuple[float, float]] | None = None, domain: str = "deterministic-mock", source: str | None = None, backend=None) -> PracticeAttempt:
        self.safety.guard(f"{skill} {domain}")
        task = PracticeTask(skill=skill, prompt=f"simulate {len(steps)} steps", kind="simulation")
        scenario = SimulationScenario(name=f"practice-{skill}", domain=domain, initial_state=SimulationState(variables=[StateVariable(name=k, value=v) for k, v in initial.items()]), actions=[SimulationAction(name=f"step-{index}", deltas=[StateVariable(name=k, value=v) for k, v in step.items()]) for index, step in enumerate(steps)], termination=TerminationCondition(max_steps=max(len(steps), 1)))
        result = (backend or MockSimulationBackend()).run(scenario)
        base = dict(task_id=task.id, skill=skill, mode=PracticeMode.SIMULATED_PRACTICE, attempt=task.prompt, provenance=provenance(source, agent="practice_engine"), limitations=SIMULATED_LIMITS + PRACTICE_LIMITS)
        if result.status.value != "COMPLETED" or not result.trace:
            return PracticeAttempt(**base, result=f"simulation {result.status.value}", passed=None, errors=list(result.limitations), feedback="No simulated evidence was produced.", score_status="NOT_EVALUABLE")
        errors = []
        for state in result.trace:
            for name, (low, high) in (bounds or {}).items():
                value = state.value(name)
                if not low <= value <= high:
                    errors.append(f"step {state.step}: {name}={value} outside [{low}, {high}]")
        final = result.trace[-1]
        for name, value in (target or {}).items():
            if abs(final.value(name) - value) > 1e-9:
                errors.append(f"final {name}={final.value(name)} expected {value}")
        if not target and not bounds:
            return PracticeAttempt(**base, result=f"simulation {result.classification.value}", passed=None, feedback="No target or constraint was supplied.", score_status="NOT_EVALUABLE")
        passed = not errors
        evidence = [SkillEvidence(skill=skill, statement=f"Mock simulation {'satisfied' if passed else 'violated'} supplied constraints.", kind=ExperienceKind.SIMULATED, passed=passed, provenance=provenance(source, agent="practice_engine"))]
        return PracticeAttempt(**base, result=f"simulation {result.classification.value}", passed=passed, errors=errors, feedback="Constraints satisfied in simulation." if passed else "Constraints violated in simulation.", score=float(len(errors)), score_status="CONSTRAINT_VIOLATION_COUNT", evidence=evidence)

    def robot_navigation(self, skill: str, start: tuple[int, int], goal: tuple[int, int], *, obstacles: tuple = (), bounds: tuple[int, int] = (10, 10), source: str | None = None) -> PracticeAttempt:
        from superagi.robotics.planning.path_planner import AStarPlanner

        try:
            path = AStarPlanner().plan(start, goal, obstacles=obstacles, bounds=bounds)
        except ValueError as exc:
            task = PracticeTask(skill=skill, prompt="robot navigation", kind="robot_navigation")
            return PracticeAttempt(task_id=task.id, skill=skill, mode=PracticeMode.SIMULATED_PRACTICE, attempt="robot navigation", result="planning failed", passed=False, errors=[str(exc)], feedback="No path in the simulated grid.", score_status="NOT_EVALUABLE", provenance=provenance(source, agent="practice_engine"), limitations=SIMULATED_LIMITS + ["No physical robot."])
        steps = [{"x": b.x - a.x, "y": b.y - a.y} for a, b in zip(path, path[1:])]
        attempt = self.simulate(skill, {"x": float(start[0]), "y": float(start[1])}, steps, target={"x": float(goal[0]), "y": float(goal[1])}, bounds={"x": (0.0, bounds[0] - 1.0), "y": (0.0, bounds[1] - 1.0)}, domain="robotics-grid-mock", source=source)
        blocked = {tuple(item) for item in obstacles}
        hits = [f"path enters obstacle {(p.x, p.y)}" for p in path if (p.x, p.y) in blocked]
        if hits:
            attempt = attempt.model_copy(update={"passed": False, "errors": attempt.errors + hits})
        return attempt.model_copy(update={"limitations": attempt.limitations + ["No physical robot.", "Grid navigation in simulation only."]})
