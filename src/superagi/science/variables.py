from .models import ScientificVariable, Parameter, Constraint, Observation
def dependencies(equation): return list(equation.variables)
