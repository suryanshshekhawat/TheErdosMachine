import math

def lcm_range(start, length):
    result = 1
    for i in range(start, start + length):
        result = result * i // math.gcd(result, i)
    return result

# Interesting: for k=4, only ONE pair of equal LCM values exists up to n=50000
# and it has gap=1 (far from needing gap>=4).
# This suggests LCM values are nearly all distinct for a given k!
# Let's check uniqueness more carefully for all k values.

print("=== Uniqueness of LCM values per k ===")
for k in range(2, 10):
    lcm_set = set()
    duplicates = 0
    for n in range(0, 50001):
        val = lcm_range(n+1, k)
        if val in lcm_set:
            duplicates += 1
        else:
            lcm_set.add(val)
    print(f"  k={k}: {50001} windows, {len(lcm_set)} unique LCM values, {duplicates} duplicates")

# Now let's think about WHY near-collisions are so rare.
# For k=3: lcm(n+1, n+2, n+3)
# The LCM of 3 consecutive integers - let's analyze the structure

print("\n=== Analysis of equal-LCM pairs for small k ===")
for k in range(3, 8):
    lcm_dict = {}
    all_pairs = []
    for n in range(0, 200001):
        val = lcm_range(n+1, k)
        if val in lcm_dict:
            for prev_n in lcm_dict[val]:
                gap = n - prev_n
                all_pairs.append((prev_n, n, gap, val))
            lcm_dict[val].append(n)
        else:
            lcm_dict[val] = [n]
    
    print(f"\n  k={k}: {len(all_pairs)} equal-LCM pairs up to n=200000")
    if all_pairs:
        all_pairs.sort(key=lambda x: -x[2])
        print(f"  Max gap: {all_pairs[0][2]} (need >= {k} for collision)")
        print(f"  Top pairs by gap:")
        for p in all_pairs[:5]:
            print(f"    n={p[0]}, m={p[1]}, gap={p[2]}, lcm={p[3]}")

# Also study the LCM value distribution - does it grow roughly as e^k * C(n+k, k)?
print("\n=== LCM growth rate analysis for k=4 ===")
k = 4
import math
vals = [(n, lcm_range(n+1, k)) for n in range(1, 101)]
print("n, lcm, log(lcm)/log(n):")
for n, v in vals[::10]:
    if n > 0 and v > 0:
        print(f"  n={n}, lcm={v}, log ratio={math.log(v)/math.log(n):.3f}")