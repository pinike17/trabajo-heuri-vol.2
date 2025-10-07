# parte-2-2.mod
# Part 2.2.2 — Maximizing Passenger Satisfaction (minimize overlapping passengers)

# Sets
set BUSES;         # buses i = 1..m
set SLOTS;         # slots s = 1..n
set WORKSHOPS;     # workshops w = 1..u

# Parameters
param c{BUSES, BUSES} >= 0;   # passengers simultaneously booked on buses i and j
param o{WORKSHOPS, SLOTS} binary; # 1 if slot s is available in workshop w, 0 otherwise

# Decision variables
var x{ i in BUSES, s in SLOTS, w in WORKSHOPS } binary;  # 1 if bus i is assigned to slot s of workshop w

# Objective: minimize total number of users assigned to the same slot in different workshops
minimize TotalOverlap:
    sum {i in BUSES, j in BUSES: i < j, s in SLOTS, w in WORKSHOPS, v in WORKSHOPS: w < v} c[i,j] * x[i,s,w] * x[j,s,v];

# Each bus assigned to exactly one slot in exactly one workshop
s.t. OneSlotPerBus {i in BUSES}:
    sum {s in SLOTS, w in WORKSHOPS} x[i,s,w] = 1;

# Each slot can host at most one bus per workshop, respecting availability
s.t. AtMostOneBusPerSlot {s in SLOTS, w in WORKSHOPS}:
    sum {i in BUSES} x[i,s,w] <= o[w,s];

