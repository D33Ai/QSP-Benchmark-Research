"""Verify the supplied numeric examples and directly check the feasible witness."""
import json
from pathlib import Path
from study import solve_recognized, check_witness

if __name__ == "__main__":
    for record in json.loads(Path(__file__).with_name("examples.json").read_text()):
        weights=[int(w,16) for w in record['weights_hex']]
        value,bits,method,rank=solve_recognized(weights)
        assert value==record['feasible'] and rank==7
        if value:
            ids=set(record['selected_indices'])
            assert all(0<=i<len(weights) for i in ids)
            assert check_witness(weights,[i in ids for i in range(len(weights))])
        print(f"{record['name']}: {value}. {len(weights)} weights, {method}.")
