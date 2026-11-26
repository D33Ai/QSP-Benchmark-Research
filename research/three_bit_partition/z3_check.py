"""Optional independent cross-check via the Z3 C library. Uses only Python stdlib + libz3."""
import ctypes
from ctypes.util import find_library
from itertools import combinations
import json
from study import FANO, CYCLE, generate


def solve_numeric(weights, timeout_ms=6000):
    lib=ctypes.CDLL(find_library("z3") or "libz3.so.4")
    ptr=ctypes.c_void_p
    def bind(name,res,args):
        fn=getattr(lib,name)
        fn.restype=res
        fn.argtypes=args
        return fn
    mkcfg=bind('Z3_mk_config',ptr,[])
    mkctx=bind('Z3_mk_context',ptr,[ptr])
    releasecfg=bind('Z3_del_config',None,[ptr])
    releasectx=bind('Z3_del_context',None,[ptr])
    evaluate=bind('Z3_eval_smtlib2_string',ctypes.c_char_p,[ptr,ctypes.c_char_p])
    rows={}
    for i,w in enumerate(weights):
        pos=0
        while w:
            w,octdigit=divmod(w,8)
            assert octdigit in (0,1)
            if octdigit:
                rows.setdefault(pos,[]).append("v"+str(i))
            pos+=1
    script=[f"(set-option :timeout {timeout_ms})"]
    script.extend(f"(declare-const v{i} Bool)" for i in range(len(weights)))
    for row in rows.values():
        assert len(row)==4
        for triple in combinations(row,3):
            script.append("(assert (or "+" ".join(triple)+"))")
            script.append("(assert (or "+" ".join("(not "+v+")" for v in triple)+"))")
    script.append("(check-sat)")
    cfg=mkcfg()
    ctx=mkctx(cfg)
    try:
        return evaluate(ctx,"\n".join(script).encode()).decode().strip()
    finally:
        releasectx(ctx)
        releasecfg(cfg)


if __name__=="__main__":
    results=[]
    for width in (1,3,5,9,21,51):
        for kind,lines,expected in [('Fano',FANO,'unsat'),('cycle',CYCLE,'sat')]:
            result=solve_numeric(generate(lines,width,111))
            if result not in (expected,'unknown'):
                raise AssertionError((kind,width,result))
            results.append(dict(family=kind,width=width,expected=expected,z3=result))
    print(json.dumps(results,indent=2))
