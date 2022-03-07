import json

from flask import Blueprint
from api.schemas import DashboardTileSchema, DashboardTileDataSchema
from api.utils import jsonify_data, get_jwt, get_json
import api.utils
from api.sxo import SXO


dashboard_api = Blueprint('dashboard', __name__)

def create_periods(row):
    response = []
    if row['column_data']['last_hour']:
        response.append('last_hour')
    if row['column_data']['last_24_hours']:
        response.append('last_24_hours')
    if row['column_data']['last_24_hours']:
        response.append('last_24_hours')
    if row['column_data']['last_7_days']:
        response.append('last_7_days')
    if row['column_data']['last_30_days']:
        response.append('last_30_days')
    if row['column_data']['last_90_days']:
        response.append('last_90_days')
    return response


def get_tile_modules(sxo):
    table = sxo.get_tile_modules()
    response = []
    for t in table:
        response.append(api.utils.set_tile(t))
    return response


def get_timeframe(req):
    if req['period'] == 'last_7_days':
        return 7
    elif req['period'] == 'last_30_days':
        return 30
    elif req['period'] == 'last_90_days':
        return 90
    return 1



def get_tile_data(sxo, req):
    modules = get_tile_modules(sxo)
    for m in modules:
        if m['id'] == req['tile_id']:
            return sxo.run_tile_workflow(req['tile_id'], m['type'])


@dashboard_api.route('/tiles', methods=['POST'])
def tiles():
    try:
        auth = get_jwt()
        sxo = SXO(auth)
        return jsonify_data(get_tile_modules(sxo))
    except:
        return jsonify_data([])


@dashboard_api.route('/tiles/tile', methods=['POST'])
def tile():
    _ = get_jwt()
    _ = get_json(DashboardTileSchema())
    return jsonify_data({})


@dashboard_api.route('/tiles/tile-data', methods=['POST'])
def tile_data():
    auth = get_jwt()
    sxo = SXO(auth)
    req = get_json(DashboardTileDataSchema())
    return jsonify_data(get_tile_data(sxo, req))

