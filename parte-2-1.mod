# parte-2-1.mod
# Part 2.2.1 — Minimization of the impact of breakdowns

# Sets
set BUSES;       # buses i = 1..m
set SLOTS;       # slots  s = 1..n  (for a single workshop)

# Parameters
param kd >= 0;        # €/km cost if a bus is assigned
param kp >= 0;        # €/passenger penalty if a bus is NOT assigned
param d{BUSES} >= 0;  # distance from bus i to the workshop (km)
param p{BUSES} >= 0;  # passengers booked on bus i

# Decision variables
var x{ i in BUSES, s in SLOTS } binary;  # 1 if bus i occupies slot s
var y{ i in BUSES } binary;              # 1 if bus i is NOT assigned

# Objective: minimize total cost (travel costs for assigned buses + penalty for unassigned buses)
minimize Cost:
    sum{ i in BUSES, s in SLOTS } kd * d[i] * x[i,s]
  + sum{ i in BUSES }           kp * p[i] * y[i];

# Each bus is either assigned to exactly one slot OR declared unassigned
s.t. OneSlotPerBus { i in BUSES }:
    sum{ s in SLOTS } x[i,s] + y[i] = 1;

# Each slot can host at most one bus
s.t. AtMostOneBusPerSlot { s in SLOTS }:
    sum{ i in BUSES } x[i,s] <= 1;

# End of model
