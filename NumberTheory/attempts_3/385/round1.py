import sympy
import numpy as np

def compute_F_analysis(limit):
    """
    For each n, F(n) = max over composite m < n of (m + p(m))
    where p(m) is the least prime factor of m.
    
    We want to check if F(n) > n for large n, and if F(n) - n -> infinity.
    
    Key insight: instead of computing F(n) for every n separately,
    we can compute for each composite m, the value m + p(m), and then
    F(n) = max of all such values for composite m < n.
    
    So let's:
    1. Compute lpf (least prime factor) for all numbers up to limit
    2. For each composite m, compute m + lpf(m)
    3. F(n) = running max of m + lpf(m) for composite m < n
    4. Check F(n) - n
    """
    
    # Sieve for least prime factor
    lpf = np.arange(limit + 1, dtype=np.int64)
    for p in range(2, int(limit**0.5) + 1):
        if lpf[p] == p:  # p is prime
            lpf[p*p::p] = np.minimum(lpf[p*p::p], p)
    
    # is_prime: lpf[m] == m (and m >= 2)
    is_composite = np.zeros(limit + 1, dtype=bool)
    is_composite[4:] = lpf[4:] != np.arange(4, limit + 1)
    # Also mark 0 and 1 as not composite
    is_composite[0] = False
    is_composite[1] = False
    
    # For each composite m, value = m + lpf[m]
    # Compute running max
    # F(n) = max over composite m < n of (m + lpf[m])
    
    # Let's compute values at composite positions
    composites = np.where(is_composite)[0]
    values = composites + lpf[composites]
    
    print(f"Total composites up to {limit}: {len(composites)}")
    print(f"First few composites and their values m+p(m):")
    for i in range(10):
        m = composites[i]
        print(f"  m={m}, lpf={lpf[m]}, m+lpf={values[i]}")
    
    # Running max of values as m increases
    running_max = np.maximum.accumulate(values)
    
    # F(n) for various n: F(n) = running_max up to the last composite < n
    # Let's sample n at various points
    
    # For each n, find index of last composite < n
    # running_max[i] = max of values[0..i] = F(composites[i]+1) essentially
    
    # Let's look at F(n) - n for n in a range
    # Sample every 1000th n from 100 to limit
    sample_ns = list(range(100, min(10001, limit), 100))
    
    print("\nn, F(n), F(n)-n:")
    for n in sample_ns[:50]:
        # find composites < n
        idx = np.searchsorted(composites, n, side='left') - 1
        if idx < 0:
            continue
        fn = running_max[idx]
        print(f"  n={n}, F(n)={fn}, F(n)-n={fn-n}")
    
    # Look at larger values
    print("\nLarger n samples:")
    large_ns = [10**4, 5*10**4, 10**5, 5*10**5, 10**6]
    for n in large_ns:
        if n > limit:
            continue
        idx = np.searchsorted(composites, n, side='left') - 1
        if idx < 0:
            continue
        fn = running_max[idx]
        print(f"  n={n}, F(n)={fn}, F(n)-n={fn-n}")
    
    # Find n where F(n) - n is minimized (most interesting cases)
    # Check all n = composites[i]+1 (just after a composite)
    fn_minus_n = running_max - (composites + 1)
    min_idx = np.argmin(fn_minus_n[:len(composites)//2])  # look in first half
    print(f"\nMin F(n)-n in range: at composite+1 where composite={composites[min_idx]}")
    print(f"  F(n)-n = {fn_minus_n[min_idx]}")
    
    # Check if F(n) > n always for n beyond some point
    # F(n) corresponds to running_max; n runs continuously
    # Let's check at every integer n from some start
    # F(n) as function of n: step function that jumps at composites
    # F(n) - n decreases between jumps (since n increases but F stays same)
    # At n = composite m+1, F(n) might jump
    
    # The minimum of F(n)-n over consecutive integers occurs just before
    # F(n) jumps, i.e., at n = next_composite - 1 or at primes/gaps
    
    # Let's track where F(n) - n could be minimal
    # Between composite m and next composite m', F stays at running_max value
    # and n increases, so F(n)-n decreases
    # minimum in interval [m+1, m') is at n = m'-1 (just before next composite)
    
    # Actually let's just scan
    print("\nScanning F(n)-n for all n in [2, 10000]:")
    scan_limit = min(10000, limit)
    current_max = 0
    min_diff = float('inf')
    min_n = -1
    
    comp_ptr = 0
    for n in range(2, scan_limit + 1):
        # Update running max if composites[comp_ptr] < n
        while comp_ptr < len(composites) and composites[comp_ptr] < n:
            current_max = max(current_max, values[comp_ptr])
            comp_ptr += 1
        if current_max > 0:
            diff = current_max - n
            if diff < min_diff:
                min_diff = diff
                min_n = n
    
    print(f"Minimum F(n)-n = {min_diff} at n = {min_n}")
    print(f"(Negative means F(n) <= n at that point)")

compute_F_analysis(100000)