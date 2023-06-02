#!/usr/bin/python3
import sys
import math
import random
import json
import time


def anneal(kids, budget, max_bid, decay_factor, kid_bid_impressions, kid_ctr_cr):
    # Simulated Annealing Algorithm
    initial_temperature, final_temperature = 500, 1e-15
    total_iterations = int(math.log(final_temperature / initial_temperature) / math.log(decay_factor))
    kid_bid_impressions = {kid: {
        bid: impressions for bid, impressions in bid_impressions.items() if float(bid) < max_bid
    } for kid, bid_impressions in kid_bid_impressions.items()}
    kid_bid_range = {kid: list(bid_impressions) for kid, bid_impressions in kid_bid_impressions.items()}
    kid_neighborhood_size = {kid: len(bid_range) for kid, bid_range in kid_bid_range.items()}
    kid_ctr = {kid: ctr_cr[0] for kid, ctr_cr in kid_ctr_cr.items()}
    kid_cr = {kid: ctr_cr[1] for kid, ctr_cr in kid_ctr_cr.items()}
    kid_bid_spend_sales = {kid: {
        bid: (
            float(bid) * impressions * kid_ctr[kid],
            impressions * kid_ctr[kid] * kid_cr[kid]
        ) for bid, impressions in bid_impressions.items()
    } for kid, bid_impressions in kid_bid_impressions.items()}

    def calculate_spend_sales(bid_selections):
        spend, sales = 0, 0
        for kid, bid in bid_selections.items():
            _spend, _sales = kid_bid_spend_sales[kid][bid]
            spend += _spend
            sales += _sales
        return spend, sales

    max_bid_selections = {kid: max(bid_impressions) for kid, bid_impressions in kid_bid_impressions.items()}
    max_spend, _ = calculate_spend_sales(max_bid_selections)

    # Initialize
    bid_selections = {kid: min(bid_impressions) for kid, bid_impressions in kid_bid_impressions.items()}
    spend, sales = calculate_spend_sales(bid_selections)
    T = initial_temperature

    for iteration in range(total_iterations):
        new_bid_selections = {}
        for kid, bid in bid_selections.items():
            if random.random() < 1 / 3:
                max_neighborhood_size = kid_neighborhood_size[kid]
                min_neighborhood_size = 2
                neighborhood_size = max_neighborhood_size - (max_neighborhood_size - min_neighborhood_size) * (
                            iteration / total_iterations)
                half_neighborhood_size = int(neighborhood_size // 2)
                bid_range = kid_bid_range[kid]
                lower_bound = max(0, bid_range.index(bid) - half_neighborhood_size)
                upper_bound = min(len(bid_range) - 1, bid_range.index(bid) + half_neighborhood_size)
                new_bid = random.choice(bid_range[lower_bound:upper_bound + 1])
                new_bid_selections[kid] = new_bid
            else:
                new_bid_selections[kid] = bid

        iteration_budget = max_spend - (max_spend - budget) * min(iteration * (5 / 3) / total_iterations, 1)
        new_spend, new_sales = calculate_spend_sales(new_bid_selections)

        if (
                (
                        new_spend <= iteration_budget and (
                        new_sales > sales
                        or random.random() < math.exp(min((new_sales - sales) / T, 709))
                )
                ) or (spend > iteration_budget and new_spend < spend)
        ):
            bid_selections = new_bid_selections
            spend, sales = new_spend, new_sales

        # Decay the temperature
        T *= decay_factor

        # if iteration % 100 == 0:
        #    print(iteration,T,iteration_budget,spend,sales)

    return {
        'bid_selections': bid_selections,
        'spend': spend,
        'sales': sales,
    }


def determine_max_bid(kids, budget, kid_bid_impressions, kid_ctr_cr):
    samples_x = []
    samples_y = []
    for i in (32, 16, 8, 4):
        if i == 32:
            X = list(i * 32 + 8 for i in range(10))
        elif not samples_y:
            return 0.5
        else:
            best_x = samples_x[samples_y.index(max(samples_y))]
            X = [best_x - i, best_x + i]
        for x in X:
            if not x >= 2:
                continue
            resp = anneal(kids, budget, x / 100, 0.995, kid_bid_impressions, kid_ctr_cr)
            if resp['spend'] > budget:
                break
            y = resp['sales']
            samples_x.append(x)
            samples_y.append(y)
            if i == 32 and y < max(samples_y) * 0.9:
                break
    return samples_x[samples_y.index(max(samples_y))] / 100


with open('annealing_test.json') as f:
    data = json.load(f)
_kids = data['kids']
budget = data['budget']
decay_factor = data['decay_factor']
_kid_bid_impressions = data['kid_bid_impressions']
_kid_ctr_cr = data['kid_ctr_cr']

num = 40
kids = _kids[:num]
kid_bid_impressions = dict()
kid_ctr_cr = dict()
for k in kids:
    kid_bid_impressions.update({k: _kid_bid_impressions[k]})
    kid_ctr_cr.update({k: _kid_ctr_cr[k]})


t = time.time_ns()
max_bid = determine_max_bid(kids, budget, kid_bid_impressions, kid_ctr_cr)
resp = anneal(kids, budget, max_bid, decay_factor, kid_bid_impressions, kid_ctr_cr)
print('time:', int(time.time_ns() - t))
print('spend:', resp['spend'])
print('sales:', resp['sales'])
