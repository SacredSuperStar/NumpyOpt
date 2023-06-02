# Python3 program to implement
# the above approach
from sys import maxsize
from typing import List

# Stores the found edges
found = []

# Stores the number of nodes
N = 0

# Stores the capacity
# of each edge
cap = []

flow = []

# Stores the cost per
# unit flow of each edge
cost = []

# Stores the distance from each node
# and picked edges for each node
dad = []
dist = []
pi = []

INF = maxsize // 2 - 1


# Function to check if it is possible to
# have a flow from the src to sink
def search(src: int, sink: int) -> bool:
    # Initialise found[] to false
    found = [False for _ in range(N)]

    # Initialise the dist[] to INF
    dist = [INF for _ in range(N + 1)]

    # Distance from the source node
    dist[src] = 0

    # Iterate until src reaches N
    while (src != N):
        best = N
        found[src] = True

        for k in range(N):

            # If already found
            if (found[k]):
                continue

            # Evaluate while flow
            # is still in supply
            if (flow[k][src] != 0):

                # Obtain the total value
                val = (dist[src] + pi[src] -
                       pi[k] - cost[k][src])

                # If dist[k] is > minimum value
                if (dist[k] > val):
                    # Update
                    dist[k] = val
                    dad[k] = src

            if (flow[src][k] < cap[src][k]):
                val = (dist[src] + pi[src] -
                       pi[k] + cost[src][k])

                # If dist[k] is > minimum value
                if (dist[k] > val):
                    # Update
                    dist[k] = val
                    dad[k] = src

            if (dist[k] < dist[best]):
                best = k

        # Update src to best for
        # next iteration
        src = best

    for k in range(N):
        pi[k] = min(pi[k] + dist[k], INF)

    # Return the value obtained at sink
    return found[sink]


# Function to obtain the maximum Flow
def getMaxFlow(capi: List[List[int]],
               costi: List[List[int]],
               src: int, sink: int) -> List[int]:
    global cap, cost, found, dist, pi, N, flow, dad
    cap = capi
    cost = costi

    N = len(capi)
    found = [False for _ in range(N)]
    flow = [[0 for _ in range(N)]
            for _ in range(N)]
    dist = [INF for _ in range(N + 1)]
    dad = [0 for _ in range(N)]
    pi = [0 for _ in range(N)]

    totflow = 0
    totcost = 0

    # If a path exist from src to sink
    while (search(src, sink)):

        # Set the default amount
        amt = INF
        x = sink

        while x != src:
            amt = min(
                amt, flow[x][dad[x]] if
                (flow[x][dad[x]] != 0) else
                cap[dad[x]][x] - flow[dad[x]][x])
            x = dad[x]

        x = sink

        while x != src:
            if (flow[x][dad[x]] != 0):
                flow[x][dad[x]] -= amt
                totcost -= amt * cost[x][dad[x]]

            else:
                flow[dad[x]][x] += amt
                totcost += amt * cost[dad[x]][x]

            x = dad[x]

        totflow += amt

    # Return pair total cost and sink
    return [totflow, totcost], flow


# Driver Code
if __name__ == "__main__":
    s = 0
    t = 4

    cap = [[0, 3, 1, 0, 3],
           [0, 0, 2, 0, 0],
           [0, 0, 0, 1, 6],
           [0, 0, 0, 0, 2],
           [0, 0, 0, 0, 0]]

    cost = [[0, 1, 0, 0, 2],
            [0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0]]

    ret, flow = getMaxFlow(cap, cost, s, t)
    import numpy as np
    cap, flow = np.array(cap), np.array(flow)
    print(np.all(flow <= cap))
    print("{} {}".format(ret[0], ret[1]))

# This code is contributed by sanjeev2552