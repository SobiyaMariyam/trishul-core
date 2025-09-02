# app/services/rudra_forecast.py
from typing import List, Tuple
from datetime import datetime, timezone
from sklearn.linear_model import LinearRegression
import numpy as np

def train_and_predict(usage: List[float]) -> Tuple[float, float]:
    """
    Simple linear regression y ~ t to predict next point.
    Returns: (prediction, slope)
    """
    if len(usage) < 2:
        return float(usage[-1] if usage else 0.0), 0.0
    X = np.arange(len(usage)).reshape(-1, 1)
    y = np.array(usage, dtype=float)
    model = LinearRegression().fit(X, y)
    next_x = np.array([[len(usage)]])
    pred = float(model.predict(next_x)[0])
    return pred, float(model.coef_[0])

def utcnow():
    return datetime.now(timezone.utc)
