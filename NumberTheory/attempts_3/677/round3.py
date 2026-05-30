import math

def lcm_range(start, length):
    result = 1
    for i in range(start, start + length):
        result = result * i // math.gcd(result, i)
    return result

# Key observation: LCM is NOT monotone, so collisions are theoretically possible.
# The window-sliding can both increase and decrease LCM.
# We need to search more carefully and at larger ranges.

# Strategy: use a hash-based approach, store all seen LCM values
# For each k, search up to n=100000

print("=== Extended search k=3..8 up to n=100000 ===")
for k in range(3, 9):
    lcm_dict = {}
    collision = None
    for n in range(0, 100001):
        val = lcm_range(n+1, k)
        if val in lcm_dict:
            prev_list = lcm_dict[val]
            for prev_n in prev_list:
                if n >= prev_n + k:
                    collision = (prev_n, n, k, val)
                    break
            if collision:
                break
            prev_list.append(n)
        else:
            lcm_dict[val] = [n]
    
    if collision:
        prev_n, n, kk, val = collision
        # Verify
        v1 = lcm_range(prev_n+1, k)
        v2 = lcm_range(n+1, k)
        print(f"  k={k}: COLLISION! n={prev_n}, m={n}, m-n={n-prev_n}, m>=n+k? {n>=prev_n+k}")
        print(f"    lcm({prev_n+1}..{prev_n+k})={v1}")
        print(f"    lcm({n+1}..{n+k})={v2}")
        print(f"    Equal: {v1==v2}")
    else:
        print(f"  k={k}: No collision up to n=100000")

# Also examine the near-miss cases: pairs with equal LCM but m < n+k (overlapping windows)
print("\n=== Near misses for k=4 (equal LCM, m < n+k) ===")
k = 4
lcm_dict = {}
near_misses = []
for n in range(0, 50000):
    val = lcm_range(n+1, k)
    if val in lcm_dict:
        for prev_n in lcm_dict[val]:
            gap = n - prev_n
            if gap > 0:
                near_misses.append((prev_n, n, gap, val))
        lcm_dict[val].append(n)
    else:
        lcm_dict[val] = [n]

print(f"Total equal-LCM pairs (any m>n) for k=4 up to n=50000: {len(near_misses)}")
if near_misses:
    print("Examples (sorted by gap):")
    near_misses.sort(key=lambda x: x[2], reverse=True)
    for nm in near_misses[:20]:
        prev_n, n, gap, val = nm
        print(f"  n={prev_n}, m={n}, gap={gap}, need gap>={k}, lcm={val}")
    print(f"  Max gap achieved: {near_misses[0][2]} (need k={k})")