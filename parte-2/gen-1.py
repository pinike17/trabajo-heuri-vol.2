#!/usr/bin/env python3
import sys, re, subprocess
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "parte-2-1.mod"

# ------------------ Parsing input ------------------
def parse_input(path):
    lines = [ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.strip().startswith("#")]
    if len(lines) < 4:
        raise ValueError("Input must have 4 lines (n m / kd kp / d_i / p_i).")

    n, m = map(int, lines[0].split())
    kd, kp = map(float, lines[1].split())
    d_vals = list(map(float, lines[2].split()))
    p_vals = list(map(float, lines[3].split()))

    if len(d_vals) != m: raise ValueError(f"Expected m={m} distances, got {len(d_vals)}.")
    if len(p_vals) != m: raise ValueError(f"Expected m={m} passenger counts, got {len(p_vals)}.")

    return n, m, kd, kp, d_vals, p_vals

# ------------------ Writing .dat ------------------
def write_dat(path, n, m, kd, kp, d_vals, p_vals):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"set BUSES := {' '.join(str(i+1) for i in range(m))};\n")
        f.write(f"set SLOTS := {' '.join(str(s+1) for s in range(n))};\n\n")
        f.write(f"param kd := {kd};\nparam kp := {kp};\n\n")
        f.write("param d :=\n")
        for i,v in enumerate(d_vals,1):
            f.write(f"  {i} {v}\n")
        f.write(";\n\n")
        f.write("param p :=\n")
        for i,v in enumerate(p_vals,1):
            f.write(f"  {i} {int(v) if float(v).is_integer() else v}\n")
        f.write(";\n")

# ------------------ Run GLPK ------------------
def run_glpsol(model, dat, out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    txt = out_dir / "glpsol.out"; sol = out_dir / "solution.sol"
    cmd = ["glpsol","-m",str(model),"-d",str(dat),"--write",str(sol),"-o",str(txt)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout); sys.stderr.write(proc.stderr)
        raise SystemExit(f"ERROR: glpsol exited with code {proc.returncode}.")
    return txt, sol

# ------------------ Parse Objective ------------------
def parse_objective(glpsol_out_txt):
    for ln in Path(glpsol_out_txt).read_text(encoding="utf-8").splitlines():
        if ln.strip().startswith("Objective:"):
            m = re.search(r"=\s*([0-9.eE+-]+)", ln)
            if m:
                return float(m.group(1))
    return None

# ------------------ Parse Assignments ------------------
def parse_assignment_from_out(glpsol_out_txt, m):
    text = Path(glpsol_out_txt).read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i,l in enumerate(text) if l.strip().startswith("No. Column name"))
    except StopIteration:
        return {}
    assign = {}
    for ln in text[start+1:]:
        ln = ln.strip()
        if not ln: break
        # Example: "3 x[1,3]       *              1             0             1"
        m1 = re.match(r"^\d+\s+([xy]\[[^\]]+\])\s+\*?\s*([0-9.eE+-]+)", ln)
        if not m1:
            if ln.startswith("Integer feasibility") or ln.startswith("KKT."):
                break
            continue
        name, val = m1.group(1), float(m1.group(2))
        if name.startswith("x["):
            mi = re.match(r"x\[(\d+),(\d+)\]", name)
            if mi and val >= 0.5:
                assign[int(mi.group(1))] = int(mi.group(2))
        elif name.startswith("y["):
            mi = re.match(r"y\[(\d+)\]", name)
            if mi and val >= 0.5 and int(mi.group(1)) not in assign:
                assign[int(mi.group(1))] = None
    return assign

# ------------------ Main ------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: ./gen-1.py INPUT_FILE OUTPUT_DAT", file=sys.stderr); sys.exit(2)

    in_path = Path(sys.argv[1]); out_dat = Path(sys.argv[2])
    n,m,kd,kp,d_vals,p_vals = parse_input(in_path)
    write_dat(out_dat, n,m,kd,kp,d_vals,p_vals)

    num_vars = m*n + m
    num_cons = m + n

    if not MODEL_PATH.exists():
        print(f"WARNING: Model file not found at {MODEL_PATH}.", file=sys.stderr)

    txt_path, sol_path = run_glpsol(MODEL_PATH, out_dat, out_dir=out_dat.parent)
    z = parse_objective(txt_path)
    assign = parse_assignment_from_out(txt_path, m)

    z_str = "N/A" if z is None else (f"{z:.6f}".rstrip('0').rstrip('.') if '.' in f"{z:.6f}" else f"{z}")
    print(f"{z_str} {num_vars} {num_cons}")
    for i in range(1, m+1):
        s = assign.get(i, None)
        if s is None:
            print(f"bus {i} -> UNASSIGNED")
        else:
            print(f"bus {i} -> slot {s}")

if __name__ == "__main__":
    main()
