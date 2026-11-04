# Tiny CSV column matching experiment

An independent, standard-library Python toy experiment inspired by OneSchema's [automatic column matching](https://www.oneschema.co/blog/customizations-dashboard) and [historical mappings](https://www.oneschema.co/blog/product-update-september-22). It does not use OneSchema code, customer files, or production metrics.

## Run

```sh
python3 column_match.py
```

## Input and comparison

The script generates 120 eight-column synthetic imports against an eight-field target schema. Some files place a generic label such as `email` before a specific `contact_email` label. Others have duplicate generic labels; headers alone cannot distinguish them. Ground truth is encoded in the generator for evaluation only.

- **Greedy:** process source columns in order and choose the best unused target by a deliberately simple header score.
- **Global:** choose the one-to-one assignment with the highest total header score using subset dynamic programming.
- **Global + review:** automatically accept assignments scoring at least 0.70 and send the rest to manual review.

## Results

| Measure | Result |
| --- | ---: |
| Imports / columns | 120 / 960 |
| Greedy column accuracy | 76.9% |
| Global column accuracy | 95.6% |
| Global + review automatic coverage | 81.2% |
| Accuracy on automatically accepted columns | 100% |
| Columns sent to review | 180 |

The exact scores reflect this designed stress workload. Duplicate generic labels have no identifying information, so no header-only method can reliably resolve them. A useful next experiment would compare sampled cell values, past user-confirmed mappings, and calibrated abstention on a more varied dataset. The question is whether those signals can reduce manual review without creating costly silent mis-mappings.

## Sources

- [OneSchema on Y Combinator](https://www.ycombinator.com/companies/oneschema)
- [Automatic matching](https://www.oneschema.co/blog/customizations-dashboard)
- [Historical mappings](https://www.oneschema.co/blog/product-update-september-22)
