from fastapi import FastAPI
from analytics import compute_confidence_bias

app = FastAPI(title="AI Confidence Calibration Service")

@app.get("/confidence-bias")
def get_confidence_bias():
    return {
        "status": "success",
        "confidence_bias": compute_confidence_bias()
    }
