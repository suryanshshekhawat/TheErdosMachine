# Too slow - need much faster approach.
# Key insight: use PARAMETRIC IDENTITIES to cover ALL n in O(1) per case,
# with a tiny fallback search only for exceptions.
#
# Known identities:
# 1) n = 4k:   4/n = 1/k = 1/(k+1) + 1/(k+1) -- not distinct
#    Better:   4/(4k) = 1/(k+1) + 1/(k*(k+1)/(2)) ... 
#    Actually: 1/k = 1/(k+1) + 1/(k+1+1) + ... use Egyptian fraction decomposition
#    Simple:   4/n = 1/(n/4) and split 1/m = 1/(m+1) + 1/(m(m+1)) -- 2 fractions
#    So 4/n = 1/(n/4+1) + 1/((n/4)(n/4+1)) -- only 2 fractions, need 3
#    Add: 1/a = 1/(a+1) + 1/(a(a+1)) recursively
#
# Key fast parametric families (from literature):
# A) n ≡ 0 mod 4: n=4k: 4/n=1/k; 1/k=1/(k+1)+1/(k+2)+1/(k+1)(k+2)/... 
#    Use: 1/k = 1/(k+1) + 1/(k(k+1)); then split 1/(k(k+1)) if needed
#    Actually simpler: 4/(4k) = 1/(k+1) + 1/(4k) + 1/(4k(k+1)) -- check:
#    1/(k+1)+1/(4k)+1/(4k(k+1)) = 4k/(4k(k+1)) + (k+1)/(4k(k+1)) + 1/(4k(k+1))
#    = (4k+k+1+1)/(4k(k+1)) = (5k+2)/(4k(k+1)) ≠ 1/k generally
#
# Let me just use the fastest known direct formula approach:
# For ANY n, one of these works:
# Type I:  if n ≡ 0 (mod 4): 4/n = 1/(n/4) -- then split via: 
#           1/m = 1/(m+1)+1/(m+1)+... need DISTINCT
# 
# FASTEST APPROACH: for each n, just try x = ceil(n/4) ONLY,
# then analytically find y by trying divisors of the remainder.

import math

def divisors_of(m):
    """Return divisors of m up to sqrt(m)"""
    divs = []
    for i in range(1, int(math.isqrt(m)) + 1):
        if m % i == 0:
            divs.append(i)
    return divs

def find_triple_fast(n):
    """
    4/n = 1/x + 1/y + 1/z with 1<=x<y<z integers
    
    For fixed x: 4/n - 1/x = (4x-n)/(nx)
    For fixed x,y: z = nx*y / (4xy - ny - nx) if positive integer
    
    Use algebraic identity: for remainder r/s = 1/y + 1/z,
    we need y such that (r*y - s) | s*y, i.e., (ry-s) | s^2/r ... 
    Actually: z = sy/(ry-s); need (ry-s)|sy
    Since gcd(ry-s, y) | s, let d=(ry-s), need d | sy.
    Key: ry - s = d => y=(d+s)/r (if r|d+s), z = s(d+s)/(rd) = s*y/d
    So enumerate divisors d of s^2 ... but s=nx can be huge.
    
    Better known trick: 4/n = 1/ceil(n/4) + (4*ceil(n/4)-n)/(n*ceil(n/4))
    Then for the remainder a/b, try y = ceil(b/a), and z falls out.
    """
    # Try parametric families first
    # Family 1: n odd => try x=n, y=n, z=n/2... 
    # Use: 4/n = 1/n + 3/n; 3/n: if 3|n, 3/n=1/(n/3); then 1/(n/3)=...
    #   if n=3k: 4/n=1/(3k)+1/(3k)+2/(3k) -- not distinct
    
    # PARAMETRIC (from Schinzel/Erdos known results):
    # Case n≡0(4): n=4a: 4/n=1/a=1/(a+1)+1/(a+2)+... need 3 distinct
    #   1/a = 1/(a+1) + 1/(a(a+1)); and 1/(a(a+1)) = 1/(a(a+1)+1)+...
    #   Or just: 4/(4a) = 1/(a+1) + 1/(4a) + ... let's compute directly
    # Case n≡1(4): 
    # Case n≡2(4): n=4a+2=2(2a+1): 4/n=2/(2a+1); 
    #   2/m = 1/m + 1/m -- not distinct; 2/m=1/((m+1)/2)+... if m odd
    #   2/(2a+1)=1/(a+1)+1/((a+1)(2a+1))
    #   so 4/n=1/(a+1)+1/((a+1)(2a+1)) -- only 2 terms; need one more split
    # Case n≡3(4):
    
    # SIMPLEST FAST APPROACH: for x in [ceil(n/4), ceil(n/4)+2*isqrt(n)],
    # for the remainder num/den, compute z directly from y=ceil(den/num):
    
    x_start = (n + 3) // 4
    
    for x in range(x_start, x_start + 2 * int(math.isqrt(n)) + 50):
        num = 4 * x - n
        den = n * x
        if num <= 0:
            continue
        g = math.gcd(num, den)
        a = num // g  # reduced numerator of remainder
        b = den // g  # reduced denominator
        # 1/y + 1/z = a/b, y>x, z>y
        # y = ceil(b/a) = smallest possible y
        y_min = max(x + 1, (b + a - 1) // a)
        # For each candidate y, z = b*y/(a*y-b)
        # z is integer iff (a*y-b) | b*y
        # Key: a*y - b | b*y => a*y-b | b*y - y*(a*y-b) ... 
        # Actually: a*y-b | b^2 (since a*y-b | a*b*y - b^2 = b*(ay-b)+b^2-... 
        # a*(b*y) - b*(a*y-b) = b^2, so a*y-b | b^2 (since gcd(a,b)=1 => a*y-b|b^2)
        # So enumerate divisors of b^2!
        # d = a*y - b => y = (d+b)/a (need a | d+b), z = b*y/d = b(d+b)/(ad)
        
        b2 = b * b
        # Find divisors of b^2 that give valid y,z
        # d must satisfy: d>0, a|(d+b), y=(d+b)/a > x, z=b(d+b)/(ad) > y
        # Also z integer: need d | b(d+b)/a * ... already handled by d|b^2 and a|d+b
        
        # Enumerate divisors of b^2
        if b2 > 10**12:
            # b^2 too large, fall back to direct y loop (limited)
            for y in range(y_min, y_min + 1000):
                ry = a * y - b
                if ry <= 0:
                    continue
                if (b * y) % ry == 0:
                    z = (b * y) // ry
                    if z > y:
                        return (x, y, z)
            continue
        
        found = None
        i = 1
        while i * i <= b2:
            if b2 % i == 0:
                for d in [i, b2 // i]:
                    if (d + b) % a == 0:
                        y = (d + b) // a
                        if y > x:
                            denom = a * d
                            numer_z = b * (d + b)
                            if numer_z % denom == 0:
                                z = numer_z // denom
                                if z > y:
                                    if found is None or y < found[0]:
                                        found = (y, z)
            i += 1
        
        if found:
            return (x, found[0], found[1])
    
    return None

# Test correctness
print("Verifying n=3..30:")
for n in range(3, 31):
    r = find_triple_fast(n)
    print(f"  n={n}: {r}")

import time
start = time.time()
failed = []
limit = 1_000_000
for n in range(3, limit + 1):
    r = find_triple_fast(n)
    if r is None:
        failed.append(n)
    if n % 100_000 == 0:
        print(f"  n={n}, time={time.time()-start:.1f}s, failures={len(failed)}")
    if time.time() - start > 50:
        print(f"  Time limit hit at n={n}")
        limit = n
        break

print(f"\nChecked up to n={limit} in {time.time()-start:.1f}s")
if failed:
    print(f"FAILURES: {failed}")
else:
    print(f"No counterexamples found!")