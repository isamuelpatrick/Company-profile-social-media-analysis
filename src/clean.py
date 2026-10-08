"""Cleaning pipeline for the Stanbic IBTC social media export (2013 to July 2023).

Every exclusion is a named rule and is logged, so the number of posts that reach
the analysis can be traced back to the raw files. Nothing is imputed: a metric a
platform does not report stays missing instead of becoming zero.
"""
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"

FILES = {
    "Facebook": "facebook.csv",
    "Twitter": "twitter.csv",
    "Instagram": "instagram.csv",
    "LinkedIn": "linkedin.csv",
}

# Metrics kept for analysis. Platform-specific ones are left missing where absent.
METRICS = ["Impressions", "Reach", "Engagements", "Likes", "Comments", "Shares", "Saves",
           "Post Link Clicks", "Video Views"]

URL_RE = re.compile(r"https?://\S+|www\.\S+|bit\.ly/\S+", re.I)
HASHTAG_RE = re.compile(r"#(\w+)")
MENTION_RE = re.compile(r"@\w+")


def to_number(s: pd.Series) -> pd.Series:
    """Parse exported numbers such as '207,378' or '3.4%' into floats."""
    s = s.astype("string").str.replace(r"[,%\s]", "", regex=True)
    return pd.to_numeric(s.replace({"": pd.NA}), errors="coerce")


def parse_dates(s: pd.Series) -> pd.Series:
    """The export is month-first ('12/17/2022 5:08 pm').

    3,978 Facebook rows were re-saved by a spreadsheet as '05/04/2019 10:01'
    (24-hour clock, zero-padded). In every one of those rows both the first and
    second fields are 12 or below, which is the signature of a spreadsheet that
    only converted dates it could read as day-first. The digits were not
    reordered, so they are parsed month-first like the rest of the file.
    """
    ampm = pd.to_datetime(s, format="%m/%d/%Y %I:%M %p", errors="coerce")
    h24 = pd.to_datetime(s, format="%m/%d/%Y %H:%M", errors="coerce")
    return ampm.fillna(h24)


def load_platform(network: str) -> tuple[pd.DataFrame, list[dict]]:
    raw = pd.read_csv(RAW / FILES[network], low_memory=False)
    log = [{"network": network, "step": "Raw export", "rows": len(raw)}]

    df = pd.DataFrame({
        "network": network,
        "post_id": raw["Post ID"].astype(str),
        "posted_at": parse_dates(raw["Date"]),
        "content_type": raw["Content Type"],
        "text": raw["Post"].fillna(""),
    })
    for m in METRICS:
        df[m.lower().replace(" ", "_")] = to_number(raw[m]) if m in raw.columns else np.nan
    df["er_reported"] = to_number(raw["Engagement Rate (per Impression)"])

    def drop(mask: pd.Series, step: str):
        nonlocal df
        df = df[~mask].copy()
        log.append({"network": network, "step": step, "rows": len(df), "removed": int(mask.sum())})

    drop(df["posted_at"].isna(), "Unreadable date")
    drop(df["impressions"].isna(), "No metrics recorded (impressions missing)")
    drop(df["impressions"] <= 0, "Zero impressions (post never delivered)")
    drop(df["engagements"].isna() | (df["engagements"] < 0),
         "Negative or missing engagements (export error)")
    drop(df["engagements"] > df["impressions"],
         "Engagements exceed impressions (impossible, export error)")
    drop(df["content_type"].isin(["Poll", "Document"]), "Content type with <5 posts")
    return df, log


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Engagement rate recomputed from counts, not taken from the export's string column.
    df["er"] = df["engagements"] / df["impressions"] * 100
    df["year"] = df["posted_at"].dt.year
    df["month"] = df["posted_at"].dt.month
    df["weekday"] = df["posted_at"].dt.day_name()
    df["hour"] = df["posted_at"].dt.hour
    df["partial_year"] = df["year"].eq(2023)

    body = df["text"].str.replace(URL_RE, "", regex=True)
    df["hashtags"] = df["text"].str.findall(HASHTAG_RE).apply(lambda t: [h.lower() for h in t])
    df["n_hashtags"] = df["hashtags"].str.len()
    df["has_hashtag"] = df["n_hashtags"] > 0
    df["has_link"] = df["text"].str.contains(URL_RE)
    df["has_mention"] = df["text"].str.contains(MENTION_RE)
    df["n_chars"] = body.str.len()
    df["n_words"] = body.str.split().str.len().fillna(0)
    df["has_question"] = body.str.contains(r"\?")
    return df


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    frames, logs = [], []
    for network in FILES:
        d, log = load_platform(network)
        frames.append(d)
        logs.extend(log)
    posts = add_features(pd.concat(frames, ignore_index=True))
    log = pd.DataFrame(logs)
    CLEAN.mkdir(parents=True, exist_ok=True)
    posts.drop(columns=["hashtags"]).assign(
        hashtags=posts["hashtags"].str.join(" ")
    ).to_csv(CLEAN / "posts_clean.csv", index=False)
    log.to_csv(CLEAN / "cleaning_log.csv", index=False)
    return posts, log


if __name__ == "__main__":
    posts, log = build()
    print(log.to_string(index=False))
    print(posts.groupby("network").size())
