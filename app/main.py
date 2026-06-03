import os
import json
import joblib
import redis
import numpy as np
from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

class InferenceStrategy(ABC):
    @abstractmethod
    def predict(self, model, features: np.ndarray) -> int: pass

class DefaultStrategy(InferenceStrategy):
    def predict(self, model, features: np.ndarray) -> int: return int(model.predict(features))

app = FastAPI()
models, reg_model, scaler = None, None, None

def load_assets():
    global models, reg_model, scaler
    if os.path.exists("best_models.joblib") and os.path.exists("reg_model.joblib") and os.path.exists("scaler.joblib"):
        models = joblib.load("best_models.joblib")
        reg_model = joblib.load("reg_model.joblib")
        scaler = joblib.load("scaler.joblib")

class HouseSchema(BaseModel):
    bedrooms: float; bathrooms: float; sqft_living: float; floors: float
    grade: float; sqft_above: float; sqft_basement: float; lat: float
    sqft_living15: float; model_type: str

@app.post("/predict")
async def infer(payload: HouseSchema):
    if models is None or reg_model is None: load_assets()
    if models is None or reg_model is None: raise HTTPException(status_code=500, detail="Models uninitialized.")

    data = payload.dict()
    strategy_name = data.pop('model_type')
    
    # Check cache for stored compound values
    cache_key = f"cache_dual:{strategy_name}:{json.dumps(data, sort_keys=True)}"
    try:
        cached_val = redis_client.get(cache_key)
        if cached_val is not None:
            return json.loads(cached_val)
    except redis.exceptions.ConnectionError: pass

    if strategy_name not in models:
        raise HTTPException(status_code=400, detail="Invalid Strategy Selection.")

    raw_features = np.array([list(data.values())])
    scaled_features = scaler.transform(raw_features)
    
    # Generate continuous valuation calculation and discrete tier category routing
    predicted_price = float(reg_model.predict(scaled_features)[0])
    prediction_class = DefaultStrategy().predict(models[strategy_name], scaled_features)

    response_payload = {
        "predicted_price": round(predicted_price, 2),
        "price_class": prediction_class,
        "source": "Live Compute Core Engine"
    }

    try:
        # Cache compound payload maps back onto Redis space
        redis_client.setex(cache_key, 3600, json.dumps({**response_payload, "source": "Redis Cache DB Layer"}))
    except redis.exceptions.ConnectionError: pass

    return response_payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
