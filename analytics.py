from supabase import create_client
from dotenv import load_dotenv
import os
from statistics import mean

# --------------------------------------------------
# Load environment variables from .env
# --------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in environment variables")

# --------------------------------------------------
# Create Supabase client
# --------------------------------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --------------------------------------------------
# Core analytics function
# --------------------------------------------------
def compute_confidence_bias(limit: int = 100):
    """
    Computes confidence drift/bias between AI confidence
    and human outcomes from ai_learning_logs table.
    """

    # Fetch recent learning logs
    response = (
        supabase
        .table("ai_learning_logs")
        .select("confidence, outcome, learning_type")
        .order("learned_at", desc=True)
        .limit(limit)
        .execute()
    )

    rows = response.data or []

    if not rows:
        return {
            "status": "NO_DATA",
            "message": "No learning logs found",
            "confidence_bias": 0.0
        }

    confidences = []
    correct_confidences = []
    wrong_confidences = []

    for row in rows:
        conf = row.get("confidence")
        outcome = row.get("outcome")

        if conf is None:
            continue

        confidences.append(conf)

        if outcome == "AI_CORRECT":
            correct_confidences.append(conf)
        elif outcome == "AI_WRONG":
            wrong_confidences.append(conf)

    avg_confidence = round(mean(confidences), 3) if confidences else 0.0
    avg_correct_confidence = round(mean(correct_confidences), 3) if correct_confidences else 0.0
    avg_wrong_confidence = round(mean(wrong_confidences), 3) if wrong_confidences else 0.0

    confidence_bias = round(avg_confidence - avg_wrong_confidence, 3)

    return {
        "status": "OK",
        "records_analyzed": len(rows),
        "avg_confidence": avg_confidence,
        "avg_correct_confidence": avg_correct_confidence,
        "avg_wrong_confidence": avg_wrong_confidence,
        "confidence_bias": confidence_bias,
        "bias_interpretation": (
            "OVERCONFIDENT"
            if confidence_bias > 0.2
            else "UNDERCONFIDENT"
            if confidence_bias < -0.2
            else "BALANCED"
        )
    }
