"""Create shareable PNG and PDF figures from derived CSV/JSON; requires matplotlib."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/stage4-ablation-efficiency"
out = REPORT / "figures"
out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
labels = {"original": "Original", "longllmlingua_2x": "Full LongLLMLingua",
    "longllmlingua_2x_no_coarse": "Without coarse question awareness",
    "longllmlingua_2x_no_fine": "Without fine question awareness",
    "longllmlingua_2x_no_dynamic": "Without dynamic budget",
    "longllmlingua_2x_no_restrict": "Without restrict",
    "longllmlingua_2x_reorder": "Reordering enabled",
    "longllmlingua_2x_no_recovery": "Without recovery"}
rows = list(csv.DictReader((REPORT / "ablation.csv").open()))
fig, ax = plt.subplots(figsize=(10, 5))
for i, r in enumerate(rows):
    x = float(r["em_percent"])
    ax.barh(i, x, color="#245c84" if r["method"] == "longllmlingua_2x" else "#83a9bf")
    ax.text(x + 1, i, f"{x:.1f}", va="center")
ax.set(yticks=range(len(rows)), yticklabels=[labels[r["method"]] for r in rows], xlim=(0, 100),
    xlabel="Best-subspan EM (%)", title="NPU ablation: fixed 100 questions, five positions, 2x")
ax.invert_yaxis(); fig.tight_layout()
for ext in ("png", "pdf"): fig.savefig(out / f"ablation.{ext}", dpi=180, bbox_inches="tight")
plt.close(fig)
eff = json.loads((REPORT / "efficiency.json").read_text())
fig, ax = plt.subplots(figsize=(11, 6))
erows = eff["table"]
for i, r in enumerate(erows):
    left = 0
    for field, color, label in (("compression_seconds_p50", "#3c78a0", "Compression p50"),
                                ("api_seconds_p50", "#e6a14a", "QA p50"),
                                ("recovery_seconds_p50", "#73a76e", "Recovery p50")):
        v = r[field] or 0
        ax.barh(i, v, left=left, color=color, label=label if i == 0 else None)
        left += v
ax.set(yticks=range(len(erows)), yticklabels=[labels.get(r["method"], r["method"]) for r in erows],
    xlabel="Stage medians (seconds; their sum is not the median end-to-end latency)",
    title=f"Efficiency: identical {eff['n_per_method']} samples/method, 910B; " +
          ("all five positions" if "20" in eff["positions"] else "partial positions"))
ax.invert_yaxis(); ax.legend(loc="lower right"); fig.tight_layout()
for ext in ("png", "pdf"): fig.savefig(out / f"efficiency.{ext}", dpi=180, bbox_inches="tight")
plt.close(fig)
main = json.loads((ROOT / "reports/stage3-main/summary.json").read_text())
fig, ax = plt.subplots(figsize=(8, 4.5))
for m in main["methods"]:
    cells = [r for r in main["groups"] if r["method"] == m["method"]]
    ax.plot([r["position"] for r in cells], [100*r["best_subspan_em"] for r in cells], marker="o", label=m["method"])
ax.set(xlabel="Answer document position", ylabel="Best-subspan EM (%)", xticks=[1,5,10,15,20],
       title="Course main comparison: 100 questions (stage-three CUDA source)")
ax.legend(fontsize=8); fig.tight_layout()
for ext in ("png", "pdf"): fig.savefig(ROOT / "reports/stage3-main" / f"positions.{ext}", dpi=180, bbox_inches="tight")
print(out)
