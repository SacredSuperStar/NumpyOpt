from altgraph.Graph import Graph
from altgraph.GraphAlgo import shortest_path
import json
import time
import numpy as np
from minimum_cost_maximum_flow import getMaxFlow



with open('annealing_test.json') as f:
    data = json.load(f)

kids = data['kids']
budget = data['budget']
decay_factor = data['decay_factor']
kid_bid_impressions = data['kid_bid_impressions']
kid_ctr_cr = data['kid_ctr_cr']

bids = set()
for bid_impressions in kid_bid_impressions.values():
    for bid in bid_impressions.keys():
        bids.add(bid)
bids = list(bids)
total_points = len(bids) + len(kids) + 2

capacity = np.zeros((total_points, total_points))
cost_sales = np.zeros((total_points, total_points))
cost_spend = np.zeros((total_points, total_points))
INF = 1e4
for i in range(total_points):
    for j in range(total_points):
        if j <= i:
            continue
        if i == 0:  # src cost and capacities
            if j < len(bids) + 1:  # if in bid group
                capacity[i][j] = INF

        elif i < len(bids) + 1:  # bid cost and capacities
            if j < total_points - 1 and j > len(bids):  # if in kid group
                kid, bid = kids[j - len(bids) - 1], bids[i - 1]
                try:
                    clicks = kid_bid_impressions[kid][bid] * kid_ctr_cr[kid][0]
                    capacity[i][j] = 1
                    cost_sales[i][j] = clicks * kid_ctr_cr[kid][1]
                    cost_spend[i][j] = clicks * float(bid)
                except KeyError:
                    continue

        elif i < total_points - 1:  # kid cost and capacities
            if j == total_points - 1:
                capacity[i][j] = 1
                cost_sales[i][j] = 0
                cost_spend[i][j] = 0
        else:
            pass

import pickle
s = time.time()
ret, flow = getMaxFlow(capacity, -cost_sales, 0, total_points - 1)
pickle.dump(flow, open('flow.pkl', 'wb'))
print(time.time() - s)
print(ret)
