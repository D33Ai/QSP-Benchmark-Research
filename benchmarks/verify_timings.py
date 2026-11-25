"""Recompute the 12-case scorecard from the released timing and verification records."""

import argparse
import json
import math
from pathlib import Path
from statistics import geometric_mean, median


def require(ok, message):
    if not ok:
        raise ValueError(message)


def verify(data):
    rows = {row['case']: row for row in data['rows']}
    runs = data['raw_runs']
    require(len(rows) == len(data['rows']) == 12, 'Expected 12 distinct fixtures')
    require([run['revision'] for run in runs] == data['order'] ==
            ['july', 'november', 'november', 'july'], 'Unexpected process order')

    observations = {case: {'july': [], 'november': []} for case in rows}
    for run in runs:
        records = run['cases']
        require(len(records) == len(rows) and {r['case'] for r in records} == rows.keys(),
                'Missing or duplicate fixture in one process')
        require(sum(r['passed'] for r in records) == run['passed'], 'Process pass count differs')
        for record in records:
            name = record['case']
            samples = record['solve_seconds']
            require(len(samples) == run['repeats'] == 5 and
                    all(math.isfinite(s) and s > 0 for s in samples), f'{name}: invalid timings')
            require(math.isclose(median(samples), record['median_solve_seconds'], rel_tol=1e-12),
                    f'{name}: process median differs')
            require(record['passed'] == (not record['issues']), f'{name}: verification status differs')
            require(record['exact_minimum_ratio'] == rows[name]['exact_ratio'],
                    f'{name}: reference objective differs')
            observations[name][run['revision']].append(record)

    passes = {'july': 0, 'november': 0}
    speedups = []
    count = 0
    print('case,july_median_ms,november_median_ms,july_pass,november_pass,verified_speedup')
    for name, row in rows.items():
        times = {}
        outcomes = {}
        for revision, records in observations[name].items():
            samples = [s for record in records for s in record['solve_seconds']]
            count += len(samples)
            times[revision] = 1000 * median(samples)
            outcomes[revision] = all(record['passed'] for record in records)
            passes[revision] += int(outcomes[revision])
            require(math.isclose(times[revision], row[f'{revision}_ms'], rel_tol=1e-12) and
                    outcomes[revision] == row[f'{revision}_pass'], f'{name}: summary differs')
        ratio = ''
        if all(outcomes.values()):
            speedup = times['july'] / times['november']
            require(math.isclose(speedup, row['verified_speedup'], rel_tol=1e-12),
                    f'{name}: speedup differs')
            speedups.append(speedup)
            ratio = f'{speedup:.2f}'
        else:
            require(row['verified_speedup'] is None, f'{name}: speedup on a failed case')
        print(f"{name},{times['july']:.4f},{times['november']:.4f},"
              f"{outcomes['july']},{outcomes['november']},{ratio}")

    mean = geometric_mean(speedups)
    require(len(speedups) == data['n_comparable'] and
            math.isclose(mean, data['comparable_geometric_mean'], rel_tol=1e-12), 'Aggregate differs')
    require(count == 240, 'Expected 240 timing samples')
    print(f"\n{count} samples; July {passes['july']}/12 passed; November {passes['november']}/12 passed; "
          f"geometric mean {mean:.2f}x across {len(speedups)} comparable cases.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, nargs='?', default=Path(__file__).with_name('raw_results.json'))
    verify(json.loads(parser.parse_args().input.read_text(encoding='utf-8')))
