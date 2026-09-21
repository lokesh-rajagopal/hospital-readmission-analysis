"""Static SVG charts for the README, drawn from results/*.csv.
Single series throughout, so one colour (slot 1), 95% CIs as muted error bars,
recessive grid, and only the extremes direct-labelled."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RES, OUT = ROOT / "results", ROOT / "charts"
SERIES, SURFACE, INK, INK2, GRID = "#2a78d6", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "svg.fonttype": "none",
})


def bars(df, labels, title, subtitle, fname, horizontal=False, ref=None, label_idx=None):
    fig, ax = plt.subplots(figsize=(7.2, 3.6 if not horizontal else 4.2))
    df = df.copy()
    # label text from the exact proportion, not the 2-dp rounded column
    exact = 100 * df["readmit_30"] / df["n"]
    y, lo, hi = df["rate_pct"], df["rate_pct"] - df["ci95_low"], df["ci95_high"] - df["rate_pct"]
    pos = range(len(df))
    if horizontal:
        ax.barh(pos, y, height=0.6, color=SERIES, zorder=2)
        ax.errorbar(y, pos, xerr=[lo, hi], fmt="none", ecolor=INK2, elinewidth=1, capsize=3, zorder=3)
        ax.set_yticks(list(pos), labels); ax.invert_yaxis()
        ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0); ax.set_xlabel("30-day readmission rate (%)")
        ax.spines["bottom"].set_visible(False); ax.tick_params(axis="y", length=0)
        for i in (label_idx or (int(y.idxmax()), int(y.idxmin()))):
            ax.text(df.loc[i, "ci95_high"] + 0.4, i, f"{exact[i]:.1f}%", va="center", fontsize=9, color=INK)
    else:
        ax.bar(pos, y, width=0.6, color=SERIES, zorder=2)
        ax.errorbar(pos, y, yerr=[lo, hi], fmt="none", ecolor=INK2, elinewidth=1, capsize=3, zorder=3)
        ax.set_xticks(list(pos), labels)
        ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0); ax.set_ylabel("30-day readmission rate (%)")
        ax.tick_params(axis="x", length=0)
        for i in (label_idx or (0, len(df) - 1)):
            ax.text(i, df.loc[i, "ci95_high"] + 0.4, f"{exact[i]:.1f}%", ha="center", fontsize=9, color=INK)
    if ref is not None:
        (ax.axvline if horizontal else ax.axhline)(ref, color=INK2, lw=1, ls=(0, (3, 3)), zorder=1)
    fig.suptitle(title, x=0.02, ha="left", fontsize=12, fontweight="bold")
    ax.set_title(subtitle, loc="left", fontsize=9, color=INK2, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / fname, format="svg")
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    overall = pd.read_csv(RES / "01_headline.csv")["rate_pct"][0]
    sub = f"Primary cohort, 95% CI shown. Dashed line: overall rate {overall:.1f}%."

    d = pd.read_csv(RES / "06_by_prior_inpatient.csv")
    bars(d, [f"{g} prior" for g in d["grp"]], "Each prior admission raises the rate",
         sub, "01_prior_inpatient.svg", ref=overall)

    d = pd.read_csv(RES / "08_by_discharge.csv")
    d = d[~d["grp"].isin(["Not recorded", "Not Mapped"]) & ~d["grp"].str.startswith("Other")].reset_index(drop=True)
    short = {"Discharged to home": "Home", "Discharged/transferred to SNF": "Skilled nursing facility",
             "Discharged/transferred to home with home health service": "Home with home health",
             "Discharged/transferred to another short term hospital": "Another short-term hospital",
             "Discharged/transferred to another rehab fac including rehab units of a hospital .": "Rehab facility",
             "Discharged/transferred to another type of inpatient care institution": "Other inpatient institution",
             "Discharged/transferred to ICF": "Intermediate care facility",
             "Left AMA": "Left against medical advice",
             "Discharged/transferred to a long term care hospital.": "Long-term care hospital"}
    d = d.sort_values("rate_pct", ascending=False).reset_index(drop=True)
    bars(d, [short.get(g, g) for g in d["grp"]], "Discharge destination tracks readmission risk",
         sub, "02_discharge.svg", horizontal=True, ref=overall)

    d = pd.read_csv(RES / "02_by_age.csv")
    bars(d, [g.strip("[)").replace("-", "–") for g in d["grp"]], "Risk climbs after 60",
         sub, "03_age.svg", ref=overall, label_idx=(5, 8))

    d = pd.read_csv(RES / "07_by_los.csv")
    bars(d, [g.split(". ")[1] for g in d["grp"]], "Longer stays, more readmissions",
         sub, "04_length_of_stay.svg", ref=overall)
    print("charts:", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
