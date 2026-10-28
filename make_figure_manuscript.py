"""Manuscript-sized figure (2 panels) and LaTeX table rows, both generated from grid_results.json."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = json.load(open("grid_results.json"))
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
STYLE = {
    "Recent window":       ("#eb6834", "s", "-",  "Recent window"),
    "Top-cited":           ("#1baf7a", "^", "--", "Top-cited"),
    "Hybrid (naive)":      ("#eda100", "D", ":",  "Naive hybrid"),
    "FIC proxy":           ("#2a78d6", "o", "-",  "FIC v1 (age cutoff)"),
    "FIC v2 (short walk)": ("#e87ba4", "P", "-.", "FIC v2 (no age cutoff)"),
}

def get(rule, fitness, T, obl):
    return [r for r in rows if r["rule"] == rule and r["fitness"] == fitness
            and r["T"] == T and r["obl"] == obl][0]

plt.rcParams.update({"font.size": 8})
fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.2), sharey=True, facecolor=SURF)
panels = [
    ("(a) Hard case, by field age", [15, 25, 40, 60], lambda rule, x: get(rule, 1.0, x, 2.0), "Field age at snapshot (years)"),
    ("(b) Hard case, 40-year field, by obliteration", [0.0, 1.0, 2.0, 4.0], lambda rule, x: get(rule, 1.0, 40, x), "Obliteration rate (per decade)"),
]
for ax, (title, xs, fn, xlabel) in zip(axes, panels):
    ax.set_facecolor(SURF)
    for rule, (c, m, ls, lab) in STYLE.items():
        ys = [fn(rule, x)["cov"] for x in xs]
        ax.plot(xs, ys, color=c, lw=1.6, ls=ls, marker=m, ms=5, mec=SURF, mew=1.0, label=lab, zorder=3)
    ax.set_title(title, loc="left", fontsize=8.5, color=INK, pad=6)
    ax.set_xlabel(xlabel, fontsize=8, color=INK2)
    ax.set_xticks(xs)
    ax.set_ylim(-0.03, 1.05)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED, labelsize=7.5, length=0)
axes[0].set_ylabel("Lineage coverage", fontsize=8, color=INK2)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=7.5, labelcolor=INK, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(rect=(0, 0.14, 1, 1))
fig.savefig("fic_sim_manuscript.png", dpi=300, facecolor=SURF)

# ---- LaTeX table rows, straight from the data
cols = [("Easy", 3.0, 40, 1.0), ("Hard", 1.0, 15, 2.0), ("Hard", 1.0, 25, 2.0), ("Hard", 1.0, 40, 2.0), ("Hard", 1.0, 60, 2.0)]
order = ["Recent window", "Top-cited", "Hybrid (naive)", "FIC proxy", "FIC v2 (short walk)"]
names = {"Recent window": "Recent window", "Top-cited": "Top-cited", "Hybrid (naive)": "Naive hybrid",
         "FIC proxy": "FIC v1 (age cutoff)", "FIC v2 (short walk)": "FIC v2 (no age cutoff)"}
lines = []
for rule in order:
    cells = [f"{get(rule, f, T, o)['cov']:.2f}" for (_, f, T, o) in cols]
    lines.append(f"{names[rule]} & " + " & ".join(cells) + r" \\")
open("manuscript_table_rows.tex", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("max SE:", round(max(r["cov_se"] for r in rows), 3))
