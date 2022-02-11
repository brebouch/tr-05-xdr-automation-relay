import json

from flask import Blueprint
from api.schemas import DashboardTileSchema, DashboardTileDataSchema
from api.utils import jsonify_data, get_jwt, get_json
import api.utils
from api.sxo import SXO


dashboard_api = Blueprint('dashboard', __name__)


def parse_output_table(table):
    response = []
    for t in table['output']['response'].values():
        try:
            response.append(t['data'])
        except:
            try:
                response.append(json.loads(t))
            except:
                continue
    if len(response) == 1:
        return response[0]
    return response

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


def create_metric_tile_data(tile_list):
    response = api.utils.get_tile_model()
    for t in tile_list:
        response['data'].append(
            api.utils.set_metric_tile_data(
                t['columndata']['title'],
                t['columndata']['icon'],
                t['columndata']['link'],
                t['columndata']['metric_value'],
            )
        )
    return response


def create_bar_tile_data(tile_list):
    keys = []
    values = []
    tile_data = {}
    response = api.utils.get_tile_model()
    output = parse_output_table(tile_list)
    for t in tile_list:
        response['data'].append(
            api.utils.set_metric_tile_data(
                t['columndata']['title'],
                t['columndata']['icon'],
                t['columndata']['link'],
                t['columndata']['metric_value'],
            )
        )
    return response

def create_markdown_tile_data(tile_list):
    response = api.utils.get_tile_model()
    for t in tile_list:
        response['data'].append(t['columndata']['markdown_line'])
    return response



def get_tile_data(sxo, req):
    modules = get_tile_modules(sxo)
    for m in modules:
        if m['id'] == req['tile_id']:
            tile = sxo.run_tile_workflow(req['tile_id'], m['type'])
            if m['type'] == 'metric_group':
                return create_metric_tile_data(tile)
            if m['type'] == 'markdown':
                return create_markdown_tile_data(tile)
            if 'bar_chart' in m['type']:
                return create_bar_tile_data(tile)



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

