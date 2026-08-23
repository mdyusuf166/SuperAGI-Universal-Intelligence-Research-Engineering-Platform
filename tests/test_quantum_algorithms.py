from superagi.quantum.algorithms import grover_search, deutsch_jozsa, quantum_fourier
def test_reference_algorithms(): assert grover_search(2,[1,2]).verification["controlled_reference"] and deutsch_jozsa(True).output["classification"]=="constant" and quantum_fourier(2).verification["valid"]
