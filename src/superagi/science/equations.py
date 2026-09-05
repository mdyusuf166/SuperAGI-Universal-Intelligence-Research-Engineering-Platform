from .models import Equation
def represent(expression: str, variables=(), limitations=()): return Equation(expression=expression, variables=list(variables), limitations=list(limitations))
