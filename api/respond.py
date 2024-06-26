from functools import partial

from flask import Blueprint

from api.schemas import ObservableSchema, ActionFormParamsSchema
from api.utils import get_json, jsonify_data

respond_api = Blueprint('respond', __name__)

get_observables = partial(get_json, schema=ObservableSchema(many=True))
get_action_form_params = partial(get_json, schema=ActionFormParamsSchema())


@respond_api.route('/respond/observables', methods=['POST'])
def respond_observables():
    return jsonify_data([])


@respond_api.route('/respond/trigger/', methods=['POST'])
def respond_trigger():
    return jsonify_data({'status': 'success'})
