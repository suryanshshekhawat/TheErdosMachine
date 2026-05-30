import math
from functools import reduce

def lcm_range(start, length):
    """Compute lcm(start, start+1, ..., start+length-1)"""
    result = 1
    for i in range(start, start + length):
        result = result * i // math.gcd(result, i)
    return result

def search_collisions(k, n_max):
    """
    Search for n < m where lcm(n+1,...,n+k) == lcm(m+1,...,m+k)
    and m >= n+k (so windows don't overlap or are at least k apart).
    """
    # Compute lcm for windows starting at n+1, i.e., window = [n+1, n+k]
    # We need m >= n+k, meaning start_m >= start_n + k
    # window for n: [n+1, ..., n+k], starts at n+1
    # window for m: [m+1, ..., m+k], starts at m+1
    # condition: m >= n+k => m+1 >= n+k+1 => start_m >= start_n + k
    
    lcm_dict = {}  # lcm_value -> list of n values
    collisions = []
    
    for n in range(0, n_max + 1):
        val = lcm_range(n + 1, k)
        if val in lcm_dict:
            for prev_n in lcm_dict[val]:
                # Check if current n >= prev_n + k
                if n >= prev_n + k:
                    collisions.append((prev_n, n, k, val))
                    if len(collisions) >= 5:
                        return collisions
            lcm_dict[val].append(n)
        else:
            lcm_dict[val] = [n]
    
    return collisions

print("Searching for collisions (equal LCM for non-overlapping windows)...")
print("Format: (n, m, k, lcm_value) where m >= n+k")
print()

found_any = False
for k in range(1, 8):
    # For small k, LCMs repeat more often, search larger range
    limit = 200 if k <= 3 else 500 if k <= 5 else 1000
    results = search_collisions(k, limit)
    if results:
        print(f"k={k}: COLLISION FOUND!")
        for r in results:
            n, m, kk, val = r
            print(f"  n={n}, m={m}, k={kk}, lcm={val}, m-n={m-n} >= k={kk}? {m-n >= kk}")
            # Verify
            v1 = lcm_range(n+1, k)
            v2 = lcm_range(m+1, k)
            print(f"  Verify: lcm({n+1}..{n+k})={v1}, lcm({m+1}..{m+k})={v2}, equal={v1==v2}")
        found_any = True
    else:
        print(f"k={k}: No collision found up to n={limit}")

if not found_any:
    print("\nNo collisions found in searched range.")

# Also check k=1 analytically: lcm({n+1}) = n+1, always distinct, trivially no collision
print("\nNote: k=1 trivially has no collision (lcm of single element is unique)")

# Show some LCM values for k=2,3 to understand growth
print("\nSample LCM values for k=2:")
for n in range(0, 20):
    print(f"  n={n}: lcm({n+1},{n+2})={lcm_range(n+1,2)}")