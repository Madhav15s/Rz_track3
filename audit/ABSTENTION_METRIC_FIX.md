# ABSTENTION METRIC FIX

Evaluating cases where the Support-Aware policy vetoed the underlying T-Learner's decision due to insufficient historical support.

**Regime**: SEVERE_POSITIVITY | **Seeds**: [10, 20, 30, 40, 50]

### Metric Definitions
- **regret_before**: `oracle_value - true_value(t_learner_action)`
- **regret_after**: `oracle_value - true_value(support_aware_action)`
- **value_saved**: `regret_before - regret_after`. A positive number means the support-aware fallback actively prevented economic loss compared to trusting the blind causal estimate.

- **Total Fallback Cases**: 3935
- **Total Regret Before (T-Learner)**: 214,505,381 paise
- **Total Regret After (Support-Aware)**: 209,665,563 paise
- **Total Value Saved**: 4,839,818 paise
