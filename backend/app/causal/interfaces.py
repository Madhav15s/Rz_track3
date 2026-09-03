from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd

class TreatmentEffectModel(ABC):
    @abstractmethod
    def fit(self, df_features: pd.DataFrame, df_treatments: pd.DataFrame, df_outcomes: pd.DataFrame):
        """Fit the causal estimator."""
        pass
        
    @abstractmethod
    def predict_effect(self, context: Dict[str, Any], action: int) -> float:
        """Predict uplift tau_a for a single context and action."""
        pass
        
    @abstractmethod
    def predict_all_effects(self, context: Dict[str, Any]) -> Dict[int, float]:
        """Predict uplift for all supported actions."""
        pass
        
    @abstractmethod
    def confidence(self, context: Dict[str, Any], action: int) -> str:
        """Return HIGH, MEDIUM, or LOW confidence for a prediction."""
        pass
        
    @abstractmethod
    def supported_actions(self) -> List[int]:
        """Return list of supported action IDs."""
        pass
        
    @abstractmethod
    def model_version(self) -> str:
        """Return the model version."""
        pass
