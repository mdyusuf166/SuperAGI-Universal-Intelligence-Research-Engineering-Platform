from superagi.education import *
def test_curriculum_path_practice_mastery_and_integrity():
 s=StudentProfile(name="Student",declared_knowledge=["Python"]);c=CurriculumManager().create("AI",[{"name":"Algorithms","prerequisites":["Python"]},{"name":"ML","prerequisites":["Algorithms"]}]);plan=LearningPathPlanner().plan(s,c,"AI research");assert len(plan.tasks)==2
 q=PracticeEngine().question("Algorithms");a=PracticeEngine().evaluate(q,q.answer);assert MasteryEngine().assess("Algorithms",[a]).label=="STRONG";assert KnowledgeGapAnalyzer().analyze(s,c)[0].topic=="ML";assert not AcademicIntegrityPolicy().assess("help with active exam")["allowed"]
