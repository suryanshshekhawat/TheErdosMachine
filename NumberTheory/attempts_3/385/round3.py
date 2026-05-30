# Pure standard library only

def smallest_prime_factor(n):
    if n < 2:
        return None
    if n % 2 == 0:
        return 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return i
        i += 2
    return n  # n is prime

def sieve_lpf(limit):
    """Least prime factor sieve"""
    lpf = list(range(limit + 1))
    p = 2
    while p * p <= limit:
        if lpf[p] == p:  # p is prime
            for q in range(p * p, limit + 1, p):
                if lpf[q] == q:
                    lpf[q] = p
        p += 1
    return lpf

def compute_F_analysis(limit):
    print(f"Computing sieve up to {limit}...")
    lpf = sieve_lpf(limit)
    
    # is_prime[n] = (lpf[n] == n) for n >= 2
    # is_composite[n] = (lpf[n] != n) for n >= 2
    
    print("Scanning composites and computing m + p(m)...")
    
    running_max = 0
    min_diff = float('inf')
    min_diff_n = -1
    
    # We'll track F(n)-n at every n
    # F(n) = running max of m+lpf[m] for composite m < n
    # We update running_max when we pass a composite
    
    # Store (n, F(n)-n) at interesting points
    results = []
    
    # Track min in windows for trend
    window_size = limit // 20
    window_mins = []
    current_window_min = float('inf')
    current_window_start = 2
    
    current_max = 0
    
    for n in range(2, limit + 1):
        # Before using F(n), note: F(n) uses composites m < n
        # current_max already updated for all composites < n
        
        if current_max > 0:
            diff = current_max - n
            if diff < min_diff:
                min_diff = diff
                min_diff_n = n
            if diff < current_window_min:
                current_window_min = diff
        
        # Window tracking
        if n % window_size == 0:
            window_mins.append((n, current_window_min))
            current_window_min = float('inf')
        
        # Now process n as composite (for future F values)
        if n >= 4 and lpf[n] != n:  # n is composite
            val = n + lpf[n]
            if val > current_max:
                current_max = val
        
        # Sample output
        if n in [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
            results.append((n, current_max, current_max - n))
    
    print("\nSample (n, F(n), F(n)-n):")
    for n, fn, diff in results:
        print(f"  n={n:>10}, F(n)={fn:>10}, F(n)-n={diff:>6}")
    
    print(f"\nOverall minimum F(n)-n = {min_diff} at n = {min_diff_n}")
    print(f"F({min_diff_n}) = {min_diff + min_diff_n}")
    
    print("\nMin F(n)-n in successive windows (trend):")
    for (wn, wmin) in window_mins:
        print(f"  Up to n={wn:>8}: min F(n)-n in window = {wmin}")
    
    if min_diff <= 0:
        print("\n*** POSSIBLE COUNTEREXAMPLE: F(n) <= n somewhere! ***")
    else:
        print(f"\nF(n) > n for ALL n in [2, {limit}]")

compute_F_analysis(500_000)