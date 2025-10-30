# parte-2-2-corrected.mod
# Minimize passengers assigned to same slot across different workshops

# Sets
set BUSES;       # buses i = 1..m
set SLOTS;       # slots s = 1..n
set WORKSHOPS;   # workshops w = 1..u

# Parameters
param c{BUSES, BUSES} >= 0;      # passengers simultaneously booked on buses i and j
param o{WORKSHOPS, SLOTS} binary; # 1 if slot s is available in workshop w

# Decision variables
var x{ i in BUSES, s in SLOTS, w in WORKSHOPS } binary;  # 1 if bus i assigned to slot s in workshop w
var y{ i in BUSES, j in BUSES, s in SLOTS: i < j } binary; # 1 if buses i and j are assigned to the same slot across workshops

# Objective: minimize total passengers sharing the same slot across workshops
minimize TotalDissatisfaction:
    sum {i in BUSES, j in BUSES, s in SLOTS: i < j} c[i,j] * y[i,j,s];

# Each bus assigned to exactly one slot in exactly one workshop
s.t. OneSlotPerBus {i in BUSES}:
    sum {s in SLOTS, w in WORKSHOPS} x[i,s,w] = 1;

# Each slot can host at most one bus per workshop, respecting availability
s.t. AtMostOneBusPerSlot {w in WORKSHOPS, s in SLOTS}:
    sum {i in BUSES} x[i,s,w] <= o[w,s];

# Linking y[i,j,s] to x: y[i,j,s] = 1 if buses i and j assigned to slot s in any two different workshops
s.t. LinkY1 {i in BUSES, j in BUSES, s in SLOTS: i < j}:
    y[i,j,s] <= sum {w in WORKSHOPS} x[i,s,w];

s.t. LinkY2 {i in BUSES, j in BUSES, s in SLOTS: i < j}:
    y[i,j,s] <= sum {w in WORKSHOPS} x[j,s,w];

s.t. LinkY3 {i in BUSES, j in BUSES, s in SLOTS: i < j}:
    y[i,j,s] >= sum {w in WORKSHOPS} x[i,s,w] + sum {w in WORKSHOPS} x[j,s,w] - 1;

end;
