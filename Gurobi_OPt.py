import json
import time

import gurobipy
from gurobipy.gurobipy import GRB
import numpy as np

with open('annealing_test.json') as f:
    data = json.load(f)

_kids = data['kids']
budget = data['budget']
_decay_factor = data['decay_factor']
_kid_bid_impressions = data['kid_bid_impressions']
_kid_ctr_cr = data['kid_ctr_cr']

num = 30
kids = _kids[:num]
kid_bid_impressions = dict()
kid_ctr_cr = dict()
for k in kids:
    kid_bid_impressions.update({k: _kid_bid_impressions[k]})
    kid_ctr_cr.update({k: _kid_ctr_cr[k]})

bids = set()
for bid_impressions in kid_bid_impressions.values():
    for bid in bid_impressions.keys():
        bids.add(bid)
bids = list(bids)
total_points = len(bids) + len(kids) + 2

cost_sales = []
cost_spend = []
kid_bid_matches = []
kid_bids = []
INF = 1e4
for i in range(len(kids)):
    temp = []
    bid_temp = []
    for j in range(len(bids)):
        kid, bid = kids[i], bids[j]
        try:
            clicks = kid_bid_impressions[kid][bid] * kid_ctr_cr[kid][0]
            cost_sales.append(clicks * kid_ctr_cr[kid][1])
            cost_spend.append(clicks * float(bid))
            temp.append(len(cost_sales) - 1)
            bid_temp.append(j)
        except KeyError:
            continue
    kid_bid_matches.append(temp)
    kid_bids.append(bid_temp)

t = time.time_ns()
cost_sales, cost_spend = np.array(cost_sales), np.array(cost_spend).reshape(1, -1)
model = gurobipy.Model()
x = model.addMVar(len(cost_sales), name="x", vtype=GRB.BINARY)
model.addMConstr(cost_spend, x, GRB.LESS_EQUAL, np.array([[budget]]))
for bid_requires in kid_bid_matches:
    model.addConstr(gurobipy.quicksum(x[i] for i in bid_requires) == 1)

model.setMObjective(None, cost_sales, 0.0, None, None, x, GRB.MAXIMIZE)
model.optimize()
print(f"Optimal objective value: {model.objVal}")

print("\n" * 100)
print("time: ", time.time_ns() - t)
x_val = x.X
values = dict()
for i in range(len(kids)):
    kid = kids[i]
    bid_requires = kid_bid_matches[i]
    for j, param_index in enumerate(bid_requires):
        if x_val[param_index] == 1:
            values.update({kid: bids[kid_bids[i][j]]})
print("bid_values:", values)
print("spend:", cost_spend @ x_val)
print("sales:", cost_sales.reshape(1, -1) @ x_val)
print("sales: ", model.objVal)
