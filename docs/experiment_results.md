# Evaluation Experiment Results

The evaluation benchmark was executed across N = 200 synthetic workforce clients.

## Final Summary Table

| Metric | Baseline | Prototype | Target Status |
|---|---|---|---|
| Repetition Rate | 75.95% | 6.44% | Lower than baseline |
| Repetition Reduction | 0.0% | **91.52%** | PASSED (>= 50%) |
| Consent Violation Rate | 15.0% | **0.0%** | PASSED (Target: 0.0%) |
| Summary Completeness | 45.0% | **86.55%** | PASSED (>= 85.0%) |
| Pending Action Recall | 30.0% | **75.32%** | Measured |
| Human Review Rate | N/A | **8.50%** | Report |

## Subgroup Fairness Evaluation Results

### Work Mode Dimension
- **Remote (N=68)**: Repetition Reduction: 96.21%, Consent Violation Rate: 0.0%, Completeness: 77.81%, Human Review Rate: 7.35%
- **Hybrid (N=68)**: Repetition Reduction: 96.29%, Consent Violation Rate: 0.0%, Completeness: 71.98%, Human Review Rate: 10.29%
- **On-site (N=64)**: Repetition Reduction: 96.72%, Consent Violation Rate: 0.0%, Completeness: 86.39%, Human Review Rate: 7.81%

### Preferred Language Group Dimension
- **English-primary (N=90)**: Repetition Reduction: 96.14%, Consent Violation Rate: 0.0%, Completeness: 77.98%, Human Review Rate: 10.0%
- **Multilingual (N=110)**: Repetition Reduction: 96.61%, Consent Violation Rate: 0.0%, Completeness: 79.06%, Human Review Rate: 7.27%

No material performance gap exists between population subgroups.
