from .models import *
class CurriculumManager:
 def __init__(self):self.curricula={}
 def create(self,name,topics):c=Curriculum(name=name,topics=[Topic(**x) if isinstance(x,dict) else x for x in topics]);self.curricula[c.id]=c;return c
class LearningPathPlanner:
 def plan(self,student,curriculum,goal):
  known=set(student.declared_knowledge);tasks=[StudyTask(topic=t.name) for t in curriculum.topics if t.name not in known];return StudyPlan(tasks=tasks,limitations=["Task ordering is a deterministic prerequisite approximation."])
class TutorEngine:
 def explain(self,topic):return {"topic":topic,"explanation":f"{topic}: begin with its prerequisites, then practice a small example.","limitations":["Educational explanation, not a substitute for instruction."]}
class PracticeEngine:
 def question(self,topic):return PracticeQuestion(topic=topic,question=f"Explain the core idea of {topic}.",answer="A student-authored explanation should identify the main concept.")
 def evaluate(self,q,response):return PracticeAttempt(question_id=q.id,correct=response.strip().lower()==q.answer.lower())
class MasteryEngine:
 def assess(self,topic,attempts):
  score=sum(a.correct for a in attempts)/len(attempts) if attempts else 0;label="STRONG" if score>=.8 else "PRACTICING" if score>=.5 else "BEGINNING";return MasteryAssessment(topic=topic,score=score,label=label,limitations=["Not an intelligence or psychological measurement."])
class KnowledgeGapAnalyzer:
 def analyze(self,student,curriculum):return [KnowledgeGap(topic=t.name,reason="Missing declared prerequisite.",evidence=t.prerequisites) for t in curriculum.topics if any(p not in student.declared_knowledge for p in t.prerequisites)]
class CodeMentor:
 def review(self,code):return {"feedback":"Review the code step by step and test small cases.","limitations":["Does not complete graded work for submission."]}
class ResearchMentor:
 def guide(self,question):return {"question":question,"guidance":"Formulate a scoped question, gather evidence, and design—not execute—an experiment.","limitations":["Hypotheses are not proven."]}
class AcademicIntegrityPolicy:
 def assess(self,text):return {"allowed":not any(x in text.lower() for x in ("active exam","cheat","submit for me")),"alternative":"Use this system for practice, explanation, and study planning."}
