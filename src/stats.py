"""Small, explicit statistical helpers used by the analysis notebook."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

RNG = np.random.default_rng(2023)


def median_ci(x, n_boot=2000, level=0.95):
    """Median with a percentile bootstrap confidence interval."""
    x = np.asarray(pd.Series(x).dropna())
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    boots = np.median(RNG.choice(x, size=(n_boot, len(x)), replace=True), axis=1)
    lo, hi = np.quantile(boots, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(np.median(x)), float(lo), float(hi)


def summarise(df, by, value="er", min_n=30):
    """Per-group post count, median and 95% CI. Groups below min_n are flagged, not hidden."""
    rows = []
    for key, g in df.groupby(by, observed=True):
        med, lo, hi = median_ci(g[value])
        rows.append({**dict(zip(by if isinstance(by, list) else [by],
                                key if isinstance(key, tuple) else (key,))),
                     "posts": len(g), "median": med, "ci_low": lo, "ci_high": hi,
                     "reliable": len(g) >= min_n})
    return pd.DataFrame(rows)


def kruskal_epsilon(df, group, value="er"):
    """Kruskal-Wallis test with epsilon-squared effect size (0 = none, 1 = total)."""
    groups = [g[value].dropna().values for _, g in df.groupby(group, observed=True) if len(g) >= 5]
    h, p = stats.kruskal(*groups)
    n = sum(len(g) for g in groups)
    return {"H": h, "p": p, "epsilon_sq": h / ((n**2 - 1) / (n + 1)), "n": n, "groups": len(groups)}


def spearman(df, x, y):
    r, p = stats.spearmanr(df[x], df[y], nan_policy="omit")
    return {"rho": r, "p": p, "n": int(df[[x, y]].dropna().shape[0])}


def rate_ratios(df, formula, offset_col="impressions"):
    """Poisson GLM with log(impressions) offset and robust (HC1) errors.

    Exponentiated coefficients are engagement-rate ratios: 1.20 means a 20% higher
    engagement rate per impression, holding the other terms constant. Robust errors
    keep the intervals honest when engagements are over-dispersed.
    """
    model = smf.glm(formula, data=df, family=sm.families.Poisson(),
                    offset=np.log(df[offset_col])).fit(cov_type="HC1")
    ci = model.conf_int()
    out = pd.DataFrame({
        "rate_ratio": np.exp(model.params),
        "ci_low": np.exp(ci[0]),
        "ci_high": np.exp(ci[1]),
        "p": model.pvalues,
    })
    return out, model
