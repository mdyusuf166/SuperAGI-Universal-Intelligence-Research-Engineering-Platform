from superagi.biomedical.dna import DNASequenceAnalyzer
analyzer = DNASequenceAnalyzer(); sequence = "ATGCGCTA"
print("COMPUTATIONAL DNA ANALYSIS")
print(analyzer.validate(sequence).model_dump()); print(analyzer.length(sequence)); print(analyzer.gc_content(sequence).model_dump()); print(analyzer.base_frequency(sequence).model_dump()); print(analyzer.reverse_complement(sequence)); print(analyzer.find_motif(sequence, "GC").model_dump())
