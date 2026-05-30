import math

def lcm_range(start, length):
    result = 1
    for i in range(start, start + length):
        result = result * i // math.gcd(result, i)
    return result

# Extend search range significantly for small k
# For k=2: lcm(n+1, n+2) = (n+1)(n+2)/gcd(n+1,n+2)
# gcd(n+1,n+2)=1 always, so lcm = (n+1)(n+2), strictly increasing -> NO collision possible!
# For k=3: let's check growth behavior

print("=== Monotonicity analysis ===")
print("\nFor k=2: lcm(n+1,n+2) = (n+1)(n+2) since consecutive integers are coprime")
print("This is strictly increasing in n, so NO collision possible for k=2.")

# Check if LCM is strictly increasing for various k
print("\nChecking if LCM is strictly increasing for k=3,4,5,6,7,8:")
for k in range(2, 9):
    strictly_inc = True
    prev_val = 0
    non_inc_examples = []
    for n in range(0, 5000):
        val = lcm_range(n+1, k)
        if val <= prev_val:
            strictly_inc = False
            non_inc_examples.append((n-1, n, prev_val, val))
            if len(non_inc_examples) >= 3:
                break
        prev_val = val
    if strictly_inc:
        print(f"  k={k}: STRICTLY INCREASING up to n=5000 (no collision possible in this range)")
    else:
        print(f"  k={k}: NOT strictly increasing! Examples: {non_inc_examples}")

# More detailed: check growth ratios to understand if LCM can ever decrease or stay same
print("\n=== LCM ratio lcm(n+1,...,n+k) / lcm(n,...,n+k-1) for k=4 ===")
k = 4
ratios = []
for n in range(1, 30):
    v1 = lcm_range(n, k)
    v2 = lcm_range(n+1, k)
    from fractions import Fraction
    r = Fraction(v2, v1)
    ratios.append((n, v1, v2, float(r)))
    print(f"  n={n}: lcm({n}..{n+k-1})={v1}, lcm({n+1}..{n+k})={v2}, ratio={float(r):.4f}")

# Theoretical: lcm(n+1,...,n+k) = lcm(n,...,n+k-1) * (n+k) / lcm_contribution
# When we slide window: add n+k, remove n
# New lcm = lcm(old_lcm / gcd(old_lcm, n), n+k) ... not simple

print("\n=== Extended search for k=3,4,5 up to n=10000 ===")
for k in [3, 4, 5]:
    lcm_dict = {}
    collision = None
    for n in range(0, 10001):
        val = lcm_range(n+1, k)
        if val in lcm_dict:
            for prev_n in lcm_dict[val]:
                if n >= prev_n + k:
                    collision = (prev_n, n, k, val)
                    break
            if collision:
                break
            lcm_dict[val].append(n)
        else:
            lcm_dict[val] = [n]
    if collision:
        print(f"  k={k}: COLLISION at {collision}")
    else:
        print(f"  k={k}: No collision up to n=10000")