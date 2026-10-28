"""Builds results/fig_dotnet_matrix.png and results/fig_python_js_sqlite.png from the CSV files."""
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OK, BAD, EDGE = "#d9f0d3", "#f4c7c3", "white"


def read(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def show(v):
    # The combining dot above (U+0307) is invisible on screen, so print the length instead.
    if "\u0307" in v:
        return f"{v.replace(chr(0x307), '')}  ({len(v)} simvol)"
    return v


def draw_table(ax, row_labels, col_labels, cells, col_w, label_w, sep_before=None):
    n_rows, n_cols = len(row_labels), len(col_labels)
    ax.set_xlim(0, label_w + col_w * n_cols)
    ax.set_ylim(n_rows + 1, 0)
    ax.axis("off")
    for j, c in enumerate(col_labels):
        ax.text(label_w + col_w * (j + 0.5), 0.5, c, ha="center", va="center", fontweight="bold", fontsize=11)
    for i, label in enumerate(row_labels):
        y = i + 1
        ax.text(0.1, y + 0.5, label, ha="left", va="center", family="monospace", fontsize=9.5)
        for j in range(n_cols):
            value, ok = cells[i][j]
            ax.add_patch(Rectangle((label_w + col_w * j, y), col_w, 1, facecolor=OK if ok else BAD, edgecolor=EDGE, lw=2))
            ax.text(label_w + col_w * (j + 0.5), y + 0.5, value, ha="center", va="center", family="monospace", fontsize=9.5)
    if sep_before is not None:
        ax.axhline(sep_before + 1, color="black", lw=1)


# ---- Figure 1: .NET under four cultures ----
rows = read("results/dotnet.csv")
cultures = ["en-US", "az-Latn-AZ", "tr-TR", "invariant"]
tests = list(dict.fromkeys(r["test"] for r in rows))
by = {(r["culture"], r["test"]): r for r in rows}
code = {r["test"]: r["code"] for r in rows}
cells = [[(show(by[(c, t)]["actual"]), by[(c, t)]["pass"] == "True") for c in cultures] for t in tests]
labels = [code[t].replace("CurrentCultureIgnoreCase", "CurrentCulture…IgnoreCase")
          .replace("CultureInfo.InvariantCulture", "Invariant").replace("(Azerbaijani word)", "(Azərbaycan sözü)") for t in tests]
first_control = next(i for i, t in enumerate(tests) if t.startswith("control"))

fig, ax = plt.subplots(figsize=(13, 0.5 * (len(tests) + 2) + 1.0), dpi=150)
draw_table(ax, labels, cultures, cells, col_w=2.2, label_w=5.6, sep_before=first_control)
fig.suptitle("Eyni .NET kodu, dörd fərqli mədəniyyət ayarında (CultureInfo.CurrentCulture)", fontsize=13, y=0.98)
fig.text(0.01, 0.01, "Yaşıl: proqramçının gözlədiyi nəticə. Qırmızı: fərqli nəticə. "
         "Xəttin altındakı sətirlər mədəniyyətdən asılı olmayan (invariant/ordinal) variantlardır.",
         fontsize=9, color="dimgray")
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
fig.savefig("results/fig_dotnet_matrix.png")
plt.close(fig)

# ---- Figure 2: Python, JavaScript, SQLite ----
SHOWN = ["az_upper", "az_lower", "az_lower_length", "az_casefold_equal", "sqlite_upper_az",
         "sqlite_nocase_az", "sqlite_like_az", "ascii_upper_az_locale", "parse_az_number"]
other = [r for r in read("results/python.csv") + read("results/javascript.csv") if r["test"] in SHOWN]
for r in other:
    if r["test"] == "az_lower":
        r["expected"] = "istiqlal  (8 simvol)"
labels = [f'{r["platform"]:<10} {r["code"]}' for r in other]
cells = [[(show(r["expected"]), True), (show(r["actual"]), r["pass"] == "True")] for r in other]
fig, ax = plt.subplots(figsize=(13, 0.5 * (len(other) + 2) + 1.0), dpi=150)
draw_table(ax, labels, ["Gözlənilən", "Alınan"], cells, col_w=2.9, label_w=6.6)
fig.suptitle("Python, JavaScript və SQLite: Azərbaycan hərfləri ilə eyni yoxlamalar", fontsize=13, y=0.98)
fig.tight_layout(rect=(0, 0.02, 1, 0.95))
fig.savefig("results/fig_python_js_sqlite.png")
plt.close(fig)
print("Saved results/fig_dotnet_matrix.png and results/fig_python_js_sqlite.png")
