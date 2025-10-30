#!/usr/bin/env python3
import sys, re, subprocess
from pathlib import Path
import math

MODEL_PATH = Path(__file__).resolve().parent / "parte-2-2.mod"

def parse_input(path):
    lines = [ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]
    n, m, u = map(int, lines[0].split())
    # Passenger overlap matrix c[i,j]
    c = [list(map(float, lines[i+1].split())) for i in range(m)]
    # Slot availability o[w,s]
    o = [list(map(int, lines[m+1 + w].split())) for w in range(u)]
    return n, m, u, c, o

def write_dat(path, n, m, u, c, o):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"set BUSES := {' '.join(str(i+1) for i in range(m))};\n")
        f.write(f"set SLOTS := {' '.join(str(s+1) for s in range(n))};\n")
        f.write(f"set WORKSHOPS := {' '.join(str(w+1) for w in range(u))};\n\n")

        f.write("param c :=\n")
        for i in range(m):
            for j in range(m):
                f.write(f"  {i+1} {j+1} {c[i][j]}\n")
        f.write(";\n\n")

        f.write("param o :=\n")
        for w in range(u):
            for s in range(n):
                f.write(f"  {w+1} {s+1} {o[w][s]}\n")
        f.write(";\n")

def run_glpsol(model, dat, out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    txt = out_dir / "glpsol.out"; sol = out_dir / "solution.sol"
    cmd = ["glpsol","-m",str(model),"-d",str(dat),"--write",str(sol),"-o",str(txt)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout); sys.stderr.write(proc.stderr)
        raise SystemExit(f"ERROR: glpsol exited with code {proc.returncode}.")
    return txt, sol

def parse_objective(glpsol_out_txt):
    for ln in Path(glpsol_out_txt).read_text(encoding="utf-8").splitlines():
        if ln.strip().startswith("Objective:"):
            m = re.search(r"=\s*([0-9.eE+-]+)", ln)
            if m:
                return float(m.group(1))
    return None

def parse_assignments(glpsol_out_txt, m):
    assign = []
    text = Path(glpsol_out_txt).read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i,l in enumerate(text) if l.strip().startswith("No. Column name"))
    except StopIteration:
        return assign
    for ln in text[start+1:]:
        ln = ln.strip()
        if not ln: break
        m1 = re.match(r"^\d+\s+(x\[\d+,\d+,\d+\])\s+\*?\s*([0-9.eE+-]+)", ln)
        if not m1: continue
        name, val = m1.group(1), float(m1.group(2))
        if val >= 0.5:
            mi = re.match(r"x\[(\d+),(\d+),(\d+)\]", name)
            if mi:
                assign.append((int(mi.group(1)), int(mi.group(2)), int(mi.group(3))))
    return assign

def main():
    if len(sys.argv) != 3:
        print("Usage: ./gen-2.py INPUT_FILE OUTPUT_DAT", file=sys.stderr); sys.exit(2)

    in_path = Path(sys.argv[1]); out_dat = Path(sys.argv[2])
    n, m, u, c, o = parse_input(in_path)
    write_dat(out_dat, n, m, u, c, o)

    if m < 2:
        num_pairs = 0
    else:
        num_pairs = math.comb(m, 2)

    num_vars = (m * n * u) + (num_pairs * n) #calculated value of variables

    num_cons = m + (n * u) + (3 * num_pairs * n) #calculated value of constraints

    if not MODEL_PATH.exists():
        print(f"WARNING: Model file not found at {MODEL_PATH}.", file=sys.stderr)

    txt_path, sol_path = run_glpsol(MODEL_PATH, out_dat, out_dir=out_dat.parent)
    z = parse_objective(txt_path)
    assign = parse_assignments(txt_path, m)

    z_str = "N/A" if z is None else (f"{z:.6f}".rstrip('0').rstrip('.') if '.' in f"{z:.6f}" else f"{z}")
    print(f"{z_str} {num_vars} {num_cons}")
    for bus, slot, workshop in assign:
        print(f"bus {bus} -> slot {slot} in workshop {workshop}")

if __name__ == "__main__":
    main()
