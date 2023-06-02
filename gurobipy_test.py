# Solve the following MIP:
#  maximize
#        x +   y + 2 z
#  subject to
#        x + 2 y + 3 z <= 4
#        x +   y       >= 1
#        x, y, z binary

import gurobipy as gp
from gurobipy.gurobipy import GRB
import numpy as np

# Create a new model
m = gp.Model()
# model = gp.Model()
# A = np.full((5, 10), 1)
# x = model.addMVar(10)
# b = np.full(5, 1)
# model.addMConstr(A, x, '=', b)

a = np.array([1, 2, 3]).reshape(1, -1)
b = np.array([1, 1, 2])
x = m.addMVar(3, name="x", vtype=GRB.BINARY)
m.addMConstr(a, x, GRB.LESS_EQUAL, np.array([[4]]))

m.setMObjective(None, b, 0.0, None, None, x, GRB.MAXIMIZE)
m.optimize()
print(f"Optimal objective value: {m.objVal}")
