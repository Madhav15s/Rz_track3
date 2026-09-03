import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from backend.app.causal.interfaces import TreatmentEffectModel

class BaseCausalEstimator(TreatmentEffectModel):
    def __init__(self):
        self.actions = [0, 1, 2, 3, 4, 5]
        self._preprocessor = None
        
    def supported_actions(self) -> List[int]:
        return self.actions
        
    def _build_preprocessor(self):
        # Specific to our synthetic dataset
        numeric_features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score']
        categorical_features = ['payment_method', 'failure_code', 'customer_value_band']
        
        return ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])

class TLearner(BaseCausalEstimator):
    def __init__(self, version="t-learner-v1"):
        super().__init__()
        self.version = version
        self.models: Dict[int, Pipeline] = {}
        
    def fit(self, df_features: pd.DataFrame, df_treatments: pd.DataFrame, df_outcomes: pd.DataFrame):
        df = df_features.merge(df_treatments, on='case_id').merge(df_outcomes, on=['case_id', 'assigned_action'])
        
        self._preprocessor = self._build_preprocessor()
        
        for a in self.actions:
            df_a = df[df['assigned_action'] == a]
            if len(df_a) == 0:
                continue
                
            X = df_a
            y = df_a['y_observed']
            
            clf = Pipeline(steps=[
                ('preprocessor', self._build_preprocessor()),
                ('classifier', LogisticRegression(max_iter=1000))
            ])
            clf.fit(X, y)
            self.models[a] = clf
            
    def _predict_proba_a(self, context_df: pd.DataFrame, a: int) -> np.ndarray:
        if a not in self.models:
            return np.zeros(len(context_df))
        return self.models[a].predict_proba(context_df)[:, 1]

    def predict_effect(self, context: Dict[str, Any], action: int) -> float:
        if action == 0:
            return 0.0
        df_ctx = pd.DataFrame([context])
        p0 = self._predict_proba_a(df_ctx, 0)
        pa = self._predict_proba_a(df_ctx, action)
        return float(pa[0] - p0[0])

    def predict_all_effects(self, context: Dict[str, Any]) -> Dict[int, float]:
        df_ctx = pd.DataFrame([context])
        p0 = self._predict_proba_a(df_ctx, 0)
        
        effects = {0: 0.0}
        for a in self.actions:
            if a == 0: continue
            pa = self._predict_proba_a(df_ctx, a)
            effects[a] = float(pa[0] - p0[0])
            
        return effects

    def confidence(self, context: Dict[str, Any], action: int) -> str:
        # Simplified confidence logic
        return "HIGH"

    def model_version(self) -> str:
        return self.version

class PropensityLearner(TLearner):
    """
    Baselines the industry standard: predicting GROSS probability of recovery.
    It returns P(Y=1|X,A=a) instead of the uplift P(Y=1|X,A=a) - P(Y=1|X,A=0).
    """
    def predict_effect(self, context: Dict[str, Any], action: int) -> float:
        df_ctx = pd.DataFrame([context])
        return float(self._predict_proba_a(df_ctx, action)[0])
        
    def predict_all_effects(self, context: Dict[str, Any]) -> Dict[int, float]:
        df_ctx = pd.DataFrame([context])
        effects = {}
        for a in self.actions:
            effects[a] = float(self._predict_proba_a(df_ctx, a)[0])
        return effects

class NaiveRecoveryPropensity(BaseCausalEstimator):
    """
    A naive observational model that trains a single Logistic Regression on (X, A) -> Y.
    It does not estimate heterogeneous uplift effectively because it lacks explicit X*A interactions.
    It represents the standard 'predict recovery probability' approach.
    """
    def __init__(self, version="naive-v1"):
        super().__init__()
        self.version = version
        self.model: Pipeline = None
        
    def fit(self, df_features: pd.DataFrame, df_treatments: pd.DataFrame, df_outcomes: pd.DataFrame):
        df = df_features.merge(df_treatments, on='case_id').merge(df_outcomes, on=['case_id', 'assigned_action'])
        
        X = df.drop(columns=['case_id', 'y_observed', 'propensity'])
        y = df['y_observed']
        
        numeric_features = ['amount_paise', 'time_since_failure_minutes', 'historical_payment_success_rate', 'engagement_score']
        categorical_features = ['payment_method', 'failure_code', 'customer_value_band', 'assigned_action']
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])
            
        self.model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(max_iter=1000))
        ])
        self.model.fit(X, y)
        
    def predict_effect(self, context: Dict[str, Any], action: int) -> float:
        ctx_a = context.copy()
        ctx_a['assigned_action'] = action
        df_ctx = pd.DataFrame([ctx_a])
        return float(self.model.predict_proba(df_ctx)[0, 1])

    def predict_all_effects(self, context: Dict[str, Any]) -> Dict[int, float]:
        effects = {}
        for a in self.actions:
            ctx_a = context.copy()
            ctx_a['assigned_action'] = a
            df_ctx = pd.DataFrame([ctx_a])
            effects[a] = float(self.model.predict_proba(df_ctx)[0, 1])
        return effects

    def confidence(self, context: Dict[str, Any], action: int) -> str:
        return "HIGH"
        
    def model_version(self) -> str:
        return self.version

class DoublyRobustLearner(BaseCausalEstimator):
    def __init__(self, version="dr-learner-v1", weight_style="clipped"):
        super().__init__()
        self.version = version
        self.weight_style = weight_style
        self.outcome_models: Dict[int, Pipeline] = {}
        self.propensity_model: Pipeline = None
        self.effect_models: Dict[int, Pipeline] = {}
        
    def fit(self, df_features: pd.DataFrame, df_treatments: pd.DataFrame, df_outcomes: pd.DataFrame):
        df = df_features.merge(df_treatments, on='case_id').merge(df_outcomes, on=['case_id', 'assigned_action'])
        
        # 1. Fit Propensity Model P(A | X)
        X_all = df
        A = df['assigned_action']
        self.propensity_model = Pipeline(steps=[
            ('preprocessor', self._build_preprocessor()),
            ('classifier', RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42))
        ])
        self.propensity_model.fit(X_all, A)
        
        # Predict propensities for all
        propensities = self.propensity_model.predict_proba(X_all)
        
        # 2. Fit Outcome Models E[Y | X, A=a]
        for a in self.actions:
            df_a = df[df['assigned_action'] == a]
            if len(df_a) == 0: continue
            X_a = df_a
            y_a = df_a['y_observed']
            
            clf = Pipeline(steps=[
                ('preprocessor', self._build_preprocessor()),
                ('classifier', LogisticRegression(max_iter=1000))
            ])
            clf.fit(X_a, y_a)
            self.outcome_models[a] = clf
            
        # 3. Calculate Pseudo-Outcomes and Fit Effect Models
        mu_0_pred = self.outcome_models[0].predict_proba(X_all)[:, 1] if 0 in self.outcome_models else np.zeros(len(X_all))
        prop_0 = propensities[:, 0]
        
        if self.weight_style == "clipped":
            prop_0 = np.clip(prop_0, 0.05, 0.95)
        elif self.weight_style == "raw":
            prop_0 = np.clip(prop_0, 1e-6, 1.0) # minimal safety against pure divide by 0
            
        Y_all = df['y_observed'].values
        A_all = df['assigned_action'].values
        
        if self.weight_style == "overlap":
            # Overlap weights: h(X) = P(A=a|X)(1-P(A=a|X))
            gamma_0 = mu_0_pred + (A_all == 0) * (Y_all - mu_0_pred) # Weighting applied later
        else:
            gamma_0 = mu_0_pred + (A_all == 0) / prop_0 * (Y_all - mu_0_pred)
        
        for a in self.actions:
            if a == 0: continue
            
            mu_a_pred = self.outcome_models[a].predict_proba(X_all)[:, 1] if a in self.outcome_models else np.zeros(len(X_all))
            prop_a = propensities[:, a]
            
            if self.weight_style == "clipped":
                prop_a = np.clip(prop_a, 0.05, 0.95)
            elif self.weight_style == "raw":
                prop_a = np.clip(prop_a, 1e-6, 1.0)
                
            if self.weight_style == "overlap":
                gamma_a = mu_a_pred + (A_all == a) * (Y_all - mu_a_pred)
                target_effect = gamma_a - gamma_0
                # ATO weights = P(A=a|X) * P(A=0|X)
                weights = prop_a * prop_0
            else:
                gamma_a = mu_a_pred + (A_all == a) / prop_a * (Y_all - mu_a_pred)
                target_effect = gamma_a - gamma_0
                weights = np.ones(len(X_all))
            
            subset_mask = (A_all == 0) | (A_all == a)
            X_subset = X_all[subset_mask]
            target_subset = target_effect[subset_mask]
            weights_subset = weights[subset_mask]
            
            reg = Pipeline(steps=[
                ('preprocessor', self._build_preprocessor()),
                ('regressor', Ridge(alpha=1.0))
            ])
            # Fit with sample weights if supported by final estimator
            X_transformed = reg.named_steps['preprocessor'].fit_transform(X_subset)
            reg.named_steps['regressor'].fit(X_transformed, target_subset, sample_weight=weights_subset)
            self.effect_models[a] = reg

    def predict_effect(self, context: Dict[str, Any], action: int) -> float:
        if action == 0: return 0.0
        df_ctx = pd.DataFrame([context])
        if action not in self.effect_models: return 0.0
        return self.effect_models[action].predict(df_ctx)[0]

    def predict_all_effects(self, context: Dict[str, Any]) -> Dict[int, float]:
        df_ctx = pd.DataFrame([context])
        effects = {0: 0.0}
        for a in self.actions:
            if a != 0:
                if a in self.effect_models:
                    effects[a] = self.effect_models[a].predict(df_ctx)[0]
                else:
                    effects[a] = 0.0
        return effects

    def confidence(self, context: Dict[str, Any], action: int) -> str:
        df_ctx = pd.DataFrame([context])
        prop = self.propensity_model.predict_proba(df_ctx)[0, action]
        if prop < 0.05: return "LOW"
        if prop > 0.15: return "HIGH"
        return "MEDIUM"

    def model_version(self) -> str:
        return self.version

class SupportAwareCausalPolicy:
    """
    Research policy that wraps a causal estimator (like T-Learner) and abstains
    if the predicted propensity (support) is below a strict threshold.
    """
    def __init__(self, causal_estimator: BaseCausalEstimator, min_support: float = 0.05):
        self.estimator = causal_estimator
        self.min_support = min_support
        self.propensity_model = None
        
    def fit(self, df_features: pd.DataFrame, df_treatments: pd.DataFrame, df_outcomes: pd.DataFrame):
        self.estimator.fit(df_features, df_treatments, df_outcomes)
        
        # Also fit a propensity model for support evaluation
        df = df_features.merge(df_treatments, on='case_id')
        X_all = df.drop(columns=['case_id', 'assigned_action', 'propensity'])
        A = df['assigned_action']
        
        # We can just use the estimator's preprocessor logic
        self.propensity_model = Pipeline(steps=[
            ('preprocessor', self.estimator._build_preprocessor()),
            ('classifier', RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42))
        ])
        self.propensity_model.fit(X_all, A)
        
    def get_best_action(self, context: Dict[str, Any], optimizer) -> Dict[str, Any]:
        """
        Replaces the normal optimizer flow.
        """
        amount = context.get('amount_paise', 0)
        df_ctx = pd.DataFrame([context])
        propensities = self.propensity_model.predict_proba(df_ctx)[0]
        
        effects = self.estimator.predict_all_effects(context)
        
        best_action = 0
        best_value = 0.0
        details = []
        
        from backend.app.policy.economic_policy import ACTION_CATALOG
        
        for a, uplift in effects.items():
            prop = propensities[a] if a < len(propensities) else 0.0
            
            # Abstain if support is insufficient
            if a != 0 and prop < self.min_support:
                uplift = 0.0
                
            cfg = ACTION_CATALOG.get(a)
            if not cfg: continue
            
            inc_value = (amount * uplift) - cfg.cost - cfg.friction - cfg.risk
            
            details.append({
                "action": a,
                "uplift": uplift,
                "incremental_value": inc_value,
                "support": prop
            })
            
            if inc_value > best_value:
                best_value = inc_value
                best_action = a
                
        return {
            "recommended_action": best_action,
            "expected_incremental_value": best_value,
            "details": details
        }
