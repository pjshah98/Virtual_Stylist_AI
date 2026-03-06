from flask import Blueprint, jsonify, request

from ..services.recommendation_service import RecommendationService


api_bp = Blueprint("api", __name__)


@api_bp.post("/recommendations")
def recommendations():
    payload = request.get_json(silent=True) or {}
    recs = RecommendationService().recommend(payload)
    return jsonify(recs)


@api_bp.post("/recommend")
def recommend():
    payload = request.get_json(silent=True) or {}
    recs = RecommendationService().recommend(payload)
    return jsonify(recs)


@api_bp.get("/presets")
def presets():
    return jsonify(RecommendationService().presets())


@api_bp.get("/colors")
def colors():
    return jsonify(RecommendationService().available_colors())

