from flask import Blueprint, jsonify


api1_blueprint = Blueprint("api1", __name__)


@api1_blueprint.route("/api/modelResult")
def api1():
    return jsonify({'person': {'name': 'Ivan'}})