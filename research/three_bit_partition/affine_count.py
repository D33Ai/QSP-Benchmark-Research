"""Exact counting formula for all inputs in the stated carry-free PARTITION class."""
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement
from random import Random
import json
from study import digit_support, generate, FANO, CYCLE


def affine_solution_count(equations, n):
    """Equations are (integer row mask, required parity)."""
    pivots = {}
    for mask, target in equations:
        while mask:
            p = mask.bit_length() - 1
            if p not in pivots:
                pivots[p] = (mask,target)
                break
            vec, rhs = pivots[p]
            mask ^= vec
            target ^= rhs
        else:
            if target:
                return 0
    return 1 << (n-len(pivots))


def affine_count(weights):
    at = defaultdict(list)
    for j,w in enumerate(weights):
        for d in digit_support(w):
            at[d].append(j)
    if any(len(js)>4 for js in at.values()):
        raise ValueError("digit frequency exceeds the promise")
    if any(len(js)%2 for js in at.values()):
        return 0
    base = []
    bad = []
    for js in at.values():
        base.append((sum(1<<j for j in js),(len(js)//2) % 2))
        if len(js)==4:
            a,b,c,_=js
            bad.append((((1<<a)^(1<<b),0), ((1<<a)^(1<<c),0)))
    total=0
    for count in range(len(bad)+1):
        sign=(-1)**count
        for subset in combinations(bad,count):
            extra=[r for flat in subset for r in flat]
            total+=sign*affine_solution_count(base+extra,len(weights))
    return total


def exact_numeric_count(weights):
    # The multiplicity matters when distinct indexed subsets give the same sum.
    freq=Counter({0:1})
    for w in weights:
        nxt=freq.copy()
        for subtotal,mult in freq.items():
            nxt[subtotal+w]+=mult
        freq=nxt
    total=sum(weights)
    return freq[total//2] if total%2==0 else 0


def row_chain(m):
    weights=[0]*(3*m+1)
    for i in range(m):
        for col in (i,i+1,m+1+i,2*m+1+i):
            weights[col]+=8**i
    return weights


def verify():
    rng=Random(80831)
    yes=no=0
    for index in range(600):
        n=rng.randint(3,13)
        w=[0]*n
        for d in range(rng.randint(2,8)):
            available=[j for j,val in enumerate(w) if val.bit_count()<3]
            if len(available)<2: break
            sizes=[2,2,4] if index%5 else [1,2,3,4]
            size=rng.choice([s for s in sizes if s<=len(available)])
            for j in rng.sample(available,size):
                w[j]+=8**d
        ws=[v for v in w if v]
        answer=affine_count(ws)
        assert answer==exact_numeric_count(ws)
        if answer: yes+=1
        else: no+=1
    small_yes=small_no=0
    weights4=[sum(8**d for d in digits) for t in (1,2,3) for digits in combinations(range(4),t)]
    for size in range(1,7):
        for numbers in combinations_with_replacement(weights4,size):
            if any(sum((w >> (3*d)) & 1 for w in numbers)>4 for d in range(4)):
                continue
            count=affine_count(numbers)
            assert count==exact_numeric_count(numbers)
            if count: small_yes+=1
            else: small_no+=1
    assert (small_yes,small_no)==(1810,21401)
    chains={}
    for m in range(1,11):
        value=affine_count(row_chain(m))
        assert value==2*3**m
        if m<=4:
            assert exact_numeric_count(row_chain(m))==value
        chains[m]=value
    core={}
    for name,lines in [('Fano',FANO),('cycle',CYCLE)]:
        weights=generate(lines,1,472)
        value=affine_count(weights)
        assert exact_numeric_count(weights)==value
        core[name]=value
    return dict(random_tests=yes+no,yes=yes,no=no,exhaustive_four_position_tests=small_yes+small_no,exhaustive_yes=small_yes,exhaustive_no=small_no,core_counts=core,chain_counts=chains)


if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
