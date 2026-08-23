import asyncio
from superagi.biomedical.pipeline import BiomedicalResearchPipeline
from superagi.research.models import ResearchQuestion

async def main():
    question = ResearchQuestion(question="How can computational molecular analysis help prioritize molecules for further biomedical research?", domain="biomedical")
    run = await BiomedicalResearchPipeline().run(question, smiles="CCO", sequence="ATGCGCTA", property_name="solubility")
    print("=" * 48); print("SUPERAGI ARC-04 BIOMEDICAL RESEARCH DEMO"); print("=" * 48)
    print("Research ID:", run.id); print("Question:", question.question)
    for label, stage in (("Evidence", "biomedical_context"), ("Molecules", "molecular_analysis"), ("Predictions", "prediction"), ("Verification", "verification")):
        print(f"{label}:", run.stage_results.get(stage))
    print("Provenance:", len(run.stage_results)); print("Safety:", run.stage_results["question_analysis"]["safety"])
    print("\nFinal classification:\nCOMPUTATIONAL RESEARCH RESULT\n\nLimitations:\nNo clinical validation.\nNo experiment executed.\nNo treatment recommendation.")

if __name__ == "__main__": asyncio.run(main())
