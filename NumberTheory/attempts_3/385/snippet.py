# Investigate the "counterexamples" where F(n)-n <= 0
# F(6) = 6 means F(6)-6 = 0, and there's another at n~275000
# Let's find ALL n where F(n)-n <= 2 and investigate carefully

def sieve_lpf(limit):
    lpf = list(range(limit + 1))
    p = 2
    while p * p <= limit:
        if lpf[p] == p:
            for q in range(p * p, limit + 1, p):
                if lpf[q] == q:
                    lpf[q] = p
        p += 1
    return lpf

def compute_detailed(limit):
    print(f"Computing sieve up to {limit}...")
    lpf = sieve_lpf(limit)
    
    current_max = 0
    small_diff_cases = []  # (n, F(n), diff) where diff <= 5
    
    for n in range(2, limit + 1):
        if current_max > 0:
            diff = current_max - n
            if diff <= 5:
                small_diff_cases.append((n, current_max, diff))
        
        # Update: process n as composite
        if n >= 4 and lpf[n] != n:
            val = n + lpf[n]
            if val > current_max:
                current_max = val
    
    print(f"\nAll cases where F(n)-n <= 5 (up to {limit}):")
    for n, fn, diff in small_diff_cases:
        # What composite m achieves F(n)?
        print(f"  n={n}, F(n)={fn}, F(n)-n={diff}")
    
    # Now let's carefully verify F(6)
    print("\n--- Careful verification of small n ---")
    current_max2 = 0
    for n in range(2, 20):
        if current_max2 > 0:
            print(f"  n={n}: F(n)={current_max2}, F(n)-n={current_max2-n}", end="")
            if current_max2 <= n:
                print(" *** F(n)<=n ***", end="")
            print()
        # What composites < n exist?
        composites_below = [(m, lpf[m], m+lpf[m]) for m in range(4, n) if lpf[m] != m]
        if composites_below:
            best = max(composites_below, key=lambda x: x[2])
            print(f"    Composites < {n}: {composites_below}")
            print(f"    Best: m={best[0]}, lpf={best[1]}, m+lpf={best[2]}")
        
        if n >= 4 and lpf[n] != n:
            val = n + lpf[n]
            if val > current_max2:
                current_max2 = val
    
    # The issue: F(n) is defined for n with composite m < n existing
    # For n=6: composites < 6 are just {4}, so F(6) = 4+2 = 6, F(6)-6=0
    # This is the BOUNDARY case. The problem says "for all sufficiently large n"
    # so small cases don't matter.
    
    # Find the n~275000 case
    print("\n--- Investigating n near 275000 ---")
    current_max3 = 0
    # First build up to 270000
    for n in range(2, 270001):
        if n >= 4 and lpf[n] != n:
            val = n + lpf[n]
            if val > current_max3:
                current_max3 = val
    
    print(f"F(270001) = {current_max3}, diff = {current_max3 - 270001}")
    
    # Now scan 270000-280000 carefully
    print("\nDetailed scan 270000-280000:")
    current_max4 = current_max3
    min_in_range = float('inf')
    min_n = -1
    for n in range(270001, 280001):
        diff = current_max4 - n
        if diff < min_in_range:
            min_in_range = diff
            min_n = n
        if diff <= 10:
            # What composite achieves current_max4?
            print(f"  n={n}, F(n)={current_max4}, diff={diff}")
        if n >= 4 and lpf[n] != n:
            val = n + lpf[n]
            if val > current_max4:
                current_max4 = val
                print(f"  ** F jumps at composite {n}: new max = {val} (lpf={lpf[n]})")
    
    print(f"\nMin diff in 270000-280000: {min_in_range} at n={min_n}")

compute_detailed(500_000)