import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = json.load(open("grid_results.json"))

# entity -> (colour, marker, linestyle, label with currency share)
STYLE = {
    "FIC proxy":           ("#2a78d6", "o", "-",  "FIC v1: age cutoff (50% recent)"),
    "Recent window":       ("#eb6834", "s", "-",  "Recent window (100% recent)"),
    "Top-cited":           ("#1baf7a", "^", "--", "Top-cited (0% recent)"),
    "Hybrid (naive)":      ("#eda100", "D", ":",  "Naive hybrid (50% recent)"),
    "FIC v2 (short walk)": ("#e87ba4", "P", "-.", "FIC v2: no age cutoff (50% recent)"),
}
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

def series(rule, xkey, fixed):
    pts = sorted((r[xkey], r["cov"], r["cov_se"]) for r in rows
                 if r["rule"] == rule and all(r[k] == v for k, v in fixed.items()))
    return [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]

panels = [
    ("A. Foundations strongly cited\n(everything citation-based works)", "T",
     dict(fitness=3.0, obl=1.0), "Field age at snapshot (years)"),
    ("B. Foundations not boosted, high\nobliteration: FIC proxy degrades", "T",
     dict(fitness=1.0, obl=2.0), "Field age at snapshot (years)"),
    ("C. Same hard case, 40-year field:\nobliteration rate sweep", "obl",
     dict(fitness=1.0, T=40), "Obliteration rate (per decade)"),
]

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.9), sharey=True, facecolor=SURF)
for ax, (title, xkey, fixed, xlabel) in zip(axes, panels):
    ax.set_facecolor(SURF)
    for rule, (c, m, ls, lab) in STYLE.items():
        x, y, se = series(rule, xkey, fixed)
        ax.plot(x, y, color=c, lw=2, ls=ls, marker=m, ms=7, mec=SURF, mew=1.5, label=lab, zorder=3)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=10)
    ax.set_xlabel(xlabel, fontsize=9.5, color=INK2)
    ax.set_ylim(-0.03, 1.05)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    x0, _, _ = series("FIC proxy", xkey, fixed)
    ax.set_xticks(x0)
axes[0].set_ylabel("Lineage coverage\n(share of true ancestors in the 20-item list)", fontsize=9.5, color=INK2)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=9.5,
           labelcolor=INK, bbox_to_anchor=(0.5, -0.01))
fig.suptitle("Recency windows lose the lineage; FIC-style rules recover much of it but do not reliably "
             "beat a naive classics-plus-recent hybrid",
             x=0.01, ha="left", fontsize=11.5, color=INK, y=1.0)
fig.text(0.01, 0.925, "Synthetic citation networks, 80 simulated topics per point, k = 20 references, 5-year recency window. "
         "Error bars omitted: SE < 0.04 everywhere.", fontsize=9, color=INK2, ha="left")
fig.tight_layout(rect=(0, 0.10, 1, 0.9))
fig.savefig("fic_sim_results.png", dpi=170, facecolor=SURF)
print("saved")

# table view of the plotted numbers (backup for pale colours)
import csv
with open("results_table.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rule", "fitness", "field_age", "obliteration", "lineage_coverage", "share_recent"])
    for r in rows:
        w.writerow([r["rule"], r["fitness"], r["T"], r["obl"], round(r["cov"], 3), round(r["cur"], 3)])
print("table saved")
