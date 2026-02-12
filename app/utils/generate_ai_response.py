from bson import ObjectId
from app.config.database import exam_results_collection

async def generate_ai_suggestions(examId, suggestion_needed):
    # ai_response = await call_ai_model(suggestion_needed)
    await exam_results_collection.update_one(
        {"examId": ObjectId(examId)},
        {"$set": {"ai_suggestions": "ai_response"}}
    )