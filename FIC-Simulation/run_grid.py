import sys, json, itertools, time
sys.path.insert(0, '.')
from fic_sim import evaluate

t0 = time.time()
rows = []
for fitness, T, obl in itertools.product([3.0, 1.0], [15, 25, 40, 60], [0.0, 1.0, 2.0, 4.0]):
    r = evaluate(T, reps=80, seed=7, obl=obl, fitness=fitness)
    for rule, d in r.items():
        rows.append(dict(fitness=fitness, T=T, obl=obl, rule=rule,
                         cov=d['cov'][0], cov_se=d['cov'][1],
                         found=d['found'][0], cur=d['cur'][0]))
json.dump(rows, open('grid_results.json', 'w'))
print('done in', round(time.time() - t0), 's;', len(rows), 'rows')
