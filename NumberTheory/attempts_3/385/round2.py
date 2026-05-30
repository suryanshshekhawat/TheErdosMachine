import numpy as np

def compute_F_analysis(limit):
    # Sieve for least prime factor
    lpf = np.arange(limit + 1, dtype=np.int64)
    for p in range(2, int(limit**0.5) + 1):
        if lpf[p] == p:  # p is prime
            for q in range(p*p, limit + 1, p):
                if lpf[q] == q:
                    lpf[q] = p

    # is_composite: not prime, not 0 or 1
    is_prime = (lpf == np.arange(limit + 1))
    is_composite = ~is_prime
    is_composite[0] = False
    is_composite[1] = False

    composites = np.where(is_composite)[0]
    values = composites + lpf[composites]  # m + p(m)

    print(f"Total composites up to {limit}: {len(composites)}")
    print("First few composites, lpf, m+p(m):")
    for i in range(15):
        m = int(composites[i])
        print(f"  m={m}, lpf={int(lpf[m])}, m+lpf={int(values[i])}")

    # Running max of values as m increases
    running_max = np.maximum.accumulate(values)

    # Scan F(n)-n for all n in [2, limit]
    # F(n) = running_max at last composite < n
    # We iterate and track minimum F(n)-n
    print("\nScanning F(n)-n for all n in [2, limit]...")
    
    # For each n, find index = searchsorted(composites, n) - 1
    # running_max[idx] = F(n)
    # We want to find min of running_max[idx] - n
    
    # The minimum F(n)-n occurs just before a new composite raises the max,
    # i.e., at n values where F(n) is flat. 
    # Concretely: between composite composites[i] and composites[i+1],
    # F(n) = running_max[i] for n in [composites[i]+1, composites[i+1]]
    # Min in that interval = running_max[i] - composites[i+1]
    
    # So check running_max[i] - composites[i+1] for all i
    diffs = running_max[:-1] - composites[1:]  # F(n) - n just before next composite
    
    min_idx = np.argmin(diffs)
    print(f"Min F(n)-n = {diffs[min_idx]} at n just before composite {composites[min_idx+1]}")
    print(f"  (F(n) = {running_max[min_idx]}, n ~ {composites[min_idx+1]})")
    
    # Also check at n = prime (prime gaps can be bad)
    # Find where F(n)-n is smallest for large n
    print("\nF(n)-n at selected large n (just before each composite):")
    step = len(composites) // 20
    for i in range(0, len(composites)-1, max(1, step)):
        fn = int(running_max[i])
        n_val = int(composites[i+1])
        print(f"  n~{n_val}, F(n)={fn}, F(n)-n={fn - n_val}")
    
    # Trend: look at min F(n)-n in windows
    window = len(composites) // 10
    print("\nMin F(n)-n in successive windows:")
    for w in range(10):
        start = w * window
        end = min((w+1)*window, len(composites)-1)
        if start >= end:
            break
        local_min_idx = np.argmin(diffs[start:end]) + start
        print(f"  Window {w}: composites[{start}..{end}], "
              f"min diff={diffs[local_min_idx]}, "
              f"at n~{composites[local_min_idx+1]}, "
              f"F(n)={running_max[local_min_idx]}")

    # Check: is F(n) > n for ALL n beyond some threshold?
    neg = np.where(diffs < 0)[0]
    if len(neg) > 0:
        print(f"\nF(n) <= n at {len(neg)} points! First at composite index {neg[0]}, n~{composites[neg[0]+1]}")
    else:
        print(f"\nF(n) > n for ALL tested n up to {limit} (in between-composite intervals)")
    
    # Show trend of min diff over large n
    print("\nOverall min F(n)-n up to each milestone:")
    milestones = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    for m in milestones:
        if m > limit:
            break
        idx = np.searchsorted(composites, m) - 1
        if idx < 1:
            continue
        local_diffs = diffs[:idx]
        print(f"  Up to n={m}: min F(n)-n = {np.min(local_diffs)}, current F(n)-n = {diffs[idx-1]}")

compute_F_analysis(2_000_000)