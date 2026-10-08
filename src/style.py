"""Shared chart style. One hue per chart where possible; small multiples instead of a
four-colour legend. The two-colour pair below passes a colour-blind separation check."""
import matplotlib.pyplot as plt

INK = "#1F2A37"
MUTED = "#6B7280"
GRID = "#E5E7EB"
PRIMARY = "#2F5D93"   # steel blue
ACCENT = "#D9822B"    # amber, used only for the contrast series
LIGHT = "#AFC6E0"

NETWORK_ORDER = ["Facebook", "Instagram", "LinkedIn", "Twitter"]


def apply():
    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelcolor": INK,
        "axes.edgecolor": GRID,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": INK,
        "legend.frameon": False,
    })
