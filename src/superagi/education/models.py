from __future__ import annotations
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field
class EM(BaseModel):model_config=ConfigDict(extra="forbid")
class StudentProfile(EM):id:UUID=Field(default_factory=uuid4);name:str;declared_knowledge:list[str]=Field(default_factory=list)
class Subject(EM):id:UUID=Field(default_factory=uuid4);name:str
class Topic(EM):id:UUID=Field(default_factory=uuid4);name:str;prerequisites:list[str]=Field(default_factory=list)
class Curriculum(EM):id:UUID=Field(default_factory=uuid4);name:str;topics:list[Topic]=Field(default_factory=list)
class StudyTask(EM):id:UUID=Field(default_factory=uuid4);topic:str;difficulty:str="moderate";status:str="PENDING"
class StudyPlan(EM):id:UUID=Field(default_factory=uuid4);tasks:list[StudyTask]=Field(default_factory=list);limitations:list[str]=Field(default_factory=list)
class PracticeQuestion(EM):id:UUID=Field(default_factory=uuid4);topic:str;question:str;answer:str;question_type:str="conceptual"
class PracticeAttempt(EM):id:UUID=Field(default_factory=uuid4);question_id:UUID;correct:bool;evidence:str="student-declared attempt"
class MasteryAssessment(EM):id:UUID=Field(default_factory=uuid4);topic:str;score:float;label:str;limitations:list[str]=Field(default_factory=list)
class KnowledgeGap(EM):id:UUID=Field(default_factory=uuid4);topic:str;reason:str;evidence:list[str]=Field(default_factory=list)
class EducationalRecommendation(EM):id:UUID=Field(default_factory=uuid4);text:str;reason:str;confidence:float;limitations:list[str]=Field(default_factory=list)
class LearningSession(EM):id:UUID=Field(default_factory=uuid4);objective:str;activities:list[str]=Field(default_factory=list);status:str="ACTIVE"
class LearningReport(EM):id:UUID=Field(default_factory=uuid4);plan:StudyPlan;gaps:list[KnowledgeGap]=Field(default_factory=list);recommendations:list[EducationalRecommendation]=Field(default_factory=list)
