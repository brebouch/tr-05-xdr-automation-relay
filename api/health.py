from flask import Blueprint
from api.sxo import SXO

from api.utils import get_jwt, jsonify_data

health_api = Blueprint('health', __name__)


@health_api.route('/health', methods=['POST'])
def health():
    auth = get_jwt()
    sxo = SXO(auth)
    #sxo.create_input_config(sxo.refer_id, 'ip', 'sxo test object')
    #sxo.run_workflow(sxo.refer_id)
    return jsonify_data({'status': 'ok'})
