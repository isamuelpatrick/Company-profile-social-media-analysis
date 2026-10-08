# What changed from version 1

Version 1 was built during a hackathon. A review found analytical errors that changed several headline conclusions. This file records each one and how version 2 handles it.

| # | Version 1 | Problem | Version 2 |
|---|---|---|---|
| 1 | Negative engagement counts and rates converted with `abs()` | A negative count is an export error. Flipping its sign invents data. | Excluded and logged as an error. |
| 2 | Missing reach, impressions and clicks filled with 0 | Zero means "nothing happened", not "not reported". It created false zero engagement rates for Twitter and LinkedIn. | Unreported metrics stay missing. Each platform is analysed on the metrics it reports. |
| 3 | Mode computed on the output of `describe()` | This takes the mode of eight summary numbers, not of the data. | Removed. Medians with confidence intervals are used instead. |
| 4 | Content types, hours, weekdays and years compared on summed totals | Totals mostly measure how often something was posted. | All comparisons are per post (medians) or rates. Post counts are always shown alongside. |
| 5 | 2020 rise attributed to COVID-19 | Posting volume rose 46% to 65% the same year, and 2023 is a partial year. | Volume and per-post rates are shown separately, 2023 is labelled partial, and no cause is claimed. |
| 6 | "Positive correlation between engagement rate and impressions" | No correlation was computed. | Spearman correlation per platform (weak, rho 0.06 to 0.22). |
| 7 | "Posts with hashtags get 50% more interactions" | Uncontrolled comparison of totals. | Poisson rate model controlling for format, year, time, length, tone and other features. Hashtags are neutral or negative. |
| 8 | Link effect on Twitter | Twitter adds a `t.co` link to every media post, so "has a link" meant "has media". | Link term dropped for Twitter, and the reason documented. |
| 9 | Random forest feature importances read as drivers | Models were never tested on unseen data, and built-in importances favour continuous variables like character count. | Time-based train/test split, a baseline for comparison, and permutation importance on the test set. |
| 10 | Notebook titled "Sentiment Analysis" | It contained no sentiment scoring. | Tone scored with VADER and spot-checked. Its limits are stated. |
| 11 | Dates parsed with `%d/%m/%Y` in the EDA after month-first parsing in cleaning | Two different date assumptions in one pipeline risk swapping day and month, which would distort month and weekday results. | One documented parser. A second date format in 3,978 Facebook rows is detected and recovered. |
| 12 | Nested folders (`Data/Facebook/Twitter/Instagram/Linkedin`) and intermediate CSVs | Hard to follow and reproduce. | Flat `data/raw` and `data/clean`, cleaning in code, one executed notebook. |
