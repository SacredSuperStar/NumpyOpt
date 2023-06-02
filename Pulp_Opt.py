import json
import time

import pulp as plp
import numpy as np

with open('annealing_test.json') as f:
    data = json.load(f)

_kids = data['kids']
budget = data['budget']
_decay_factor = data['decay_factor']
_kid_bid_impressions = data['kid_bid_impressions']
_kid_ctr_cr = data['kid_ctr_cr']

num = 600
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

t = time.time()
cost_sales, cost_spend = np.array(cost_sales), np.array(cost_spend)

problem = plp.LpProblem("Maximize", plp.LpMaximize)
x_vars = {i: plp.LpVariable(cat=plp.LpBinary, name="x_{0}".format(i)) for i in range(len(cost_sales))}
problem += plp.lpSum(x_vars[i] * cost_spend[i] for i in range(len(cost_sales))) <= budget

for bid_requires in kid_bid_matches:
    problem += plp.lpSum(x_vars[i] for i in bid_requires) == 1
problem += plp.lpSum(x_vars[i] * cost_sales[i] for i in range(len(cost_sales)))
status = problem.solve()
x = np.zeros(len(cost_sales))
for i in range(len(cost_sales)):
    x[i] = plp.value(x_vars[i])
print("time: ", time.time() - t)
values = dict()
for i in range(len(kids)):
    kid = kids[i]
    bid_requires = kid_bid_matches[i]
    for j, param_index in enumerate(bid_requires):
        if x[param_index] == 1:
            values.update({kid: bids[kid_bids[i][j]]})
print("bid_values:", values)
json.dump(values, open("output.json", 'wt'))
print("spend:", cost_spend.reshape(1, -1) @ x)
print("sales:", cost_sales.reshape(1, -1) @ x)
