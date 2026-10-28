"""
Stage 1 prototype: does function-based (FIC-style) source selection recover a
field's intellectual lineage better than recency-based selection?

Step 1  simulate_topic()  : synthetic citation network with a planted lineage
Step 2  select_*()        : competing reference-selection rules
Step 3  evaluate()        : lineage coverage and currency, averaged over replicates
Step 4  sensitivity grids : vary the generative assumptions

Planted lineage per topic: F (foundational) <- I1 <- I2 <- I3 (influential bridges).
Ground truth "ancestors" = the chain nodes that exist at the snapshot time.
The FIC-style rule NEVER sees the planted labels, only the observable graph
(publication time, in-degree, who cites whom).
"""
import numpy as np

CHAIN_YEARS = [0, 8, 18, 28]  # nominal creation years of F, I1, I2, I3


# ---------------------------------------------------------------- Step 1
def simulate_topic(T, rng, base_rate=5.0, growth=0.04, m=12, tau=8.0,
                   obl=1.0, fitness=3.0, p_direct=0.5):
    """Simulate one topic for T years and return the network at time T.

    tau      : aging time-scale (years) of ordinary citation attractiveness
    obl      : obliteration rate. Direct citation probability of a chain node
               decays as p_direct * exp(-obl * age_in_decades)
    fitness  : multiplicative attractiveness boost for chain nodes
    """
    counts = rng.poisson(base_rate * (1 + growth) ** np.arange(T))
    cap = int(counts.sum() + 20)
    t = np.zeros(cap)
    indeg = np.zeros(cap)
    fit = np.ones(cap)
    level = -np.ones(cap, dtype=int)
    refs = []
    chain_year = {0: 0}
    for j, yr in enumerate(CHAIN_YEARS[1:], start=1):
        chain_year[j] = yr + int(rng.integers(-2, 3))
    chain_idx = {}
    n = 0
    for y in range(T):
        events = [-1] * int(counts[y])
        events += [lvl for lvl, yy in chain_year.items() if yy == y]
        rng.shuffle(events)
        for lvl in events:
            now = y + rng.random()
            if n == 0:
                sel = set()
            else:
                age = now - t[:n]
                w = (indeg[:n] + 1.0) * np.exp(-age / tau) * fit[:n]
                k = min(m, n)
                if k < n:
                    keys = np.log(w) + rng.gumbel(size=n)
                    sel = set(np.argpartition(-keys, k - 1)[:k].tolist())
                else:
                    sel = set(range(n))
                if lvl >= 1 and (lvl - 1) in chain_idx:
                    sel.add(chain_idx[lvl - 1])          # lineage link
                for l, ci in chain_idx.items():          # direct, decaying cites
                    if rng.random() < p_direct * np.exp(-obl * (now - t[ci]) / 10.0):
                        sel.add(ci)
            arr = np.array(sorted(sel), dtype=int)
            if arr.size:
                indeg[arr] += 1
            refs.append(arr)
            t[n] = now
            if lvl >= 0:
                fit[n] = fitness
                level[n] = lvl
                chain_idx[lvl] = n
            n += 1
    return dict(t=t[:n], indeg=indeg[:n], level=level[:n], refs=refs, T=T)


# ---------------------------------------------------------------- Step 2
def _topk(score, k, rng):
    score = score + rng.random(score.size) * 1e-6          # random tie-break
    k = min(k, score.size)
    return np.argpartition(-score, k - 1)[:k]


def select_random(net, k, W, rng):
    return rng.choice(net["t"].size, size=min(k, net["t"].size), replace=False)


def select_recent_window(net, k, W, rng):
    age = net["T"] - net["t"]
    cand = np.where(age <= W)[0]
    if cand.size >= k:
        return rng.choice(cand, size=k, replace=False)
    extra = _topk(-age, k, rng)                              # most recent overall
    return np.unique(np.concatenate([cand, extra]))[:k]


def select_recency_weighted(net, k, W, rng):
    age = net["T"] - net["t"]
    keys = -age / W + rng.gumbel(size=age.size)
    return np.argpartition(-keys, k - 1)[:k]


def select_top_cited(net, k, W, rng):
    return _topk(net["indeg"].astype(float), k, rng)


def select_fic_proxy(net, k, W, rng, old_age=15, n_found=5, n_infl=5):
    """FIC-style rule using observable features only.

    foundational proxy : old papers (age >= old_age) with highest in-degree
    influential proxy  : mid-age papers that cite a foundational-proxy paper,
                         ranked by in-degree (a crude 'bridge' score)
    contemporary       : recent papers (age <= W), ranked by in-degree
    Unfilled slots are topped up with the highest in-degree papers left over.
    """
    t, indeg, refs, T = net["t"], net["indeg"], net["refs"], net["T"]
    age = T - t
    n = t.size
    chosen = []

    old = np.where(age >= old_age)[0]
    found = old[_topk(indeg[old].astype(float), n_found, rng)] if old.size else np.array([], int)
    chosen += found.tolist()

    mid = np.where((age > W) & (age < old_age))[0]
    if mid.size and old.size:
        top_old = np.zeros(n, bool)
        top_old[old[_topk(indeg[old].astype(float), 10, rng)]] = True
        bridge = np.array([top_old[refs[i]].any() if refs[i].size else False for i in mid])
        score = indeg[mid] * bridge
        pick = mid[_topk(score.astype(float), n_infl, rng)]
        chosen += [i for i in pick.tolist() if i not in chosen]

    n_cont = k - len(chosen)
    rec = np.where(age <= W)[0]
    if rec.size and n_cont > 0:
        pick = rec[_topk(indeg[rec].astype(float), n_cont, rng)]
        chosen += [i for i in pick.tolist() if i not in chosen]

    if len(chosen) < k:                                       # top-up
        left = np.setdiff1d(np.arange(n), chosen)
        chosen += left[_topk(indeg[left].astype(float), k - len(chosen), rng)].tolist()
    return np.array(chosen[:k])


def select_hybrid(net, k, W, rng):
    """Naive hybrid: half top-cited, half random recent. No age bands, no bridge
    logic. This is the fair competitor for FIC: does FIC's three-function
    structure add anything beyond 'some classics plus some recent work'?"""
    age = net["T"] - net["t"]
    half = k // 2
    top = _topk(net["indeg"].astype(float), half, rng)
    rec = np.setdiff1d(np.where(age <= W)[0], top)
    if rec.size >= k - half:
        rec = rng.choice(rec, size=k - half, replace=False)
    return np.unique(np.concatenate([top, rec]))[:k]


def _edges(net):
    """Cache citing->cited edge arrays for the network."""
    if "edges" not in net:
        src = np.concatenate([np.full(r.size, i, dtype=int) for i, r in enumerate(net["refs"])]
                             or [np.array([], int)])
        dst = np.concatenate(net["refs"]) if len(net["refs"]) else np.array([], int)
        net["edges"] = (src, dst.astype(int))
    return net["edges"]


def ancestry_scores(net, recent_mask, d=0.85, iters=40):
    """Personalised PageRank that starts at recent papers and walks BACKWARD along
    reference links. A paper scores high when much of the recent literature is
    intellectually descended from it, directly or through intermediaries.
    No age cutoff is used: only the definition of 'recent' (the review's window)."""
    n = net["t"].size
    src, dst = _edges(net)
    r0 = recent_mask.astype(float)
    r0 /= r0.sum()
    outdeg = np.bincount(src, minlength=n).astype(float)
    score = r0.copy()
    for _ in range(iters):
        flow = np.where(outdeg[src] > 0, d * score[src] / np.maximum(outdeg[src], 1), 0.0)
        new = np.bincount(dst, weights=flow, minlength=n)
        dangling = d * score[outdeg == 0].sum()
        score = (1 - d) * r0 + new + dangling * r0
    return score


def select_fic_v2(net, k, W, rng, d=0.85):
    """Threshold-free FIC-style rule, using only observable graph structure.

    contemporary slots : most-cited recent papers (half the list)
    foundational slots : highest 'ancestry' score among non-recent papers, i.e.
                         the work the recent literature descends from
    influential slots  : non-recent papers that sit BETWEEN the picks: they cite a
                         strong ancestor and are themselves cited by recent work
                         (bridge boost applied to the ancestry score)
    """
    t, indeg, refs, T = net["t"], net["indeg"], net["refs"], net["T"]
    n = t.size
    age = T - t
    recent = age <= W
    if recent.sum() == 0 or (~recent).sum() == 0:
        return select_top_cited(net, k, W, rng)
    anc = ancestry_scores(net, recent, d=d)
    old_idx = np.where(~recent)[0]

    # bridge boost: how many of a paper's references are strong ancestors?
    top_anc = np.zeros(n, bool)
    top_anc[old_idx[_topk(anc[old_idx], min(10, old_idx.size), rng)]] = True
    cites_anc = np.array([top_anc[refs[i]].sum() if refs[i].size else 0 for i in range(n)], float)
    old_score = anc * (1.0 + cites_anc)

    n_cont = k // 2
    cont = np.where(recent)[0]
    cont_pick = cont[_topk(indeg[cont].astype(float), min(n_cont, cont.size), rng)]
    old_pick = old_idx[_topk(old_score[old_idx], min(k - cont_pick.size, old_idx.size), rng)]
    sel = np.concatenate([old_pick, cont_pick])
    return sel[:k]


RULES = {
    "Random": select_random,
    "Recent window": select_recent_window,
    "Recency-weighted": select_recency_weighted,
    "Top-cited": select_top_cited,
    "Hybrid (naive)": select_hybrid,
    "FIC proxy": select_fic_proxy,
    "FIC v2 (long walk)": lambda net, k, W, rng: select_fic_v2(net, k, W, rng, d=0.85),
    "FIC v2 (short walk)": lambda net, k, W, rng: select_fic_v2(net, k, W, rng, d=0.4),
}


# ---------------------------------------------------------------- Step 3
def evaluate(T, reps=200, k=20, W=5, seed=0, **sim_kw):
    """Mean lineage coverage, foundation recall and currency per rule."""
    rng = np.random.default_rng(seed)
    out = {r: dict(cov=[], found=[], cur=[]) for r in RULES}
    for _ in range(reps):
        net = simulate_topic(T, rng, **sim_kw)
        truth = set(np.where(net["level"] >= 0)[0].tolist())
        f_idx = np.where(net["level"] == 0)[0]
        age = net["T"] - net["t"]
        for name, fn in RULES.items():
            sel = fn(net, k, W, rng)
            s = set(sel.tolist())
            out[name]["cov"].append(len(s & truth) / len(truth))
            out[name]["found"].append(float(f_idx[0] in s))
            out[name]["cur"].append(float((age[sel] <= W).mean()))
    res = {}
    for name, d in out.items():
        res[name] = {key: (np.mean(v), np.std(v, ddof=1) / np.sqrt(len(v))) for key, v in d.items()}
    return res
