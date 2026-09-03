# CausalRecover Dashboard

The CausalRecover Dashboard is a React/Vite-based presentation layer built to provide Razorpay Operations / Human Judges with total transparency into the AI's decision-making loop.

## Design Philosophy
1. **Evidence over Magic:** The UI does not use chat windows or claim "AI Magic." It displays verifiable support thresholds, confidence intervals, and economic math.
2. **Strict Guardrails:** The frontend possesses zero mutation authority. Clicking "Execute" dispatches a request that must still survive the deterministic Policy Governor in the backend.
3. **No Oracle Leakage:** Ground truth (e.g., $Y(0)...Y(5)$) is completely withheld from the live decision console, appearing only in the dedicated Evaluation View.

## Core Views
1. **Executive Overview:** The hero metric is *Net Incremental Revenue Generated* (stripping away Natural Recovery to prove true AI value).
2. **Causal Decision Console:** Exposes the heterogeneous treatment effects. For each action, displays the expected marginal uplift, whether the data distribution supports it, and whether the Governor authorized it.
3. **Incident Intelligence:** Tracks real-time API degradations affecting the counterfactual logic.
4. **Recovery Strategy:** Analyzes the distribution of actions (e.g., how often `RETRY_LATER` is chosen over `HUMAN_ESCALATION`).
5. **Safety / Governor:** Proves that the AI operates within bounded constraints (Policy Violations = 0).
6. **Execution / Razorpay:** Tracks the flow from `PROPOSED` -> `APPROVED` -> `PENDING VERIFICATION` -> `VERIFIED RECOVERED`. Explicitly labels SIMULATED vs RAZORPAY TEST MODE.
7. **Audit Trail:** Time-stamped logs of every system transition.
8. **Evaluation:** Renders the Canonical 5-Seed Benchmark proving causal superiority.
9. **Causal Explainer:** A visual aid breaking down natural vs treatment recovery for non-ML judges.

## Stack
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Lucide React (Icons)
