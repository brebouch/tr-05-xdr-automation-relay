import json
from datetime import datetime, timedelta
from flask import Blueprint
from api.schemas import DashboardTileSchema, DashboardTileDataSchema
from api.utils import jsonify_data, get_jwt, get_json
import api.utils
from api.sxo import SXO
from api.tiles import LineChart
from api.tiles import DonutChart
from api.tiles import MarkdownTile
from api.tiles import MetricTile
from api.tiles import BarChart



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


def get_metric_tile(tile_data):
    tile = MetricTile()
    data = []
    for r in tile_data['table_rows']:
        data.append(r['column_data'])
    tile.generate_tile(data)
    return tile.mod


def get_line_chart_tile(tile_data):
    tile = LineChart()
    scale = ''
    for v in tile_data['instance']['variables']:
        if v['properties']['scope'] == 'output' and v['properties']['name'] == 'Chart Scale':
            scale = v['properties']['value']
    if scale == '':
        return {}
    data = []
    for r in tile_data['table_rows']:
        data.append(r['column_data'])
    tile.generate_tile(data, scale)
    return tile.mod


def get_bar_graph_tile(tile_data):
    key_type = 'string'
    color_scale = 'Default'
    x_unit = 'Default'
    tile = BarChart()
    data = []
    for v in tile_data['instance']['variables']:
        if v['properties']['scope'] == 'output' and v['properties']['name'] == 'Key Type':
            key_type = v['properties']['value']
        elif v['properties']['scope'] == 'output' and v['properties']['name'] == 'Color Scale':
            color_scale = v['properties']['value']
        elif v['properties']['scope'] == 'output' and v['properties']['name'] == 'X-Unit':
            x_unit = v['properties']['value']
    for r in tile_data['table_rows']:
        data.append(r['column_data'])
    tile.generate_tile(key_type, data, color_scale, x_unit)
    return tile.mod


def get_donut_tile(tile_data):
    inner_label = ''
    outer_label = ''
    tile = DonutChart()
    data = []
    for v in tile_data['instance']['variables']:
        if v['properties']['scope'] == 'output' and v['properties']['name'] == 'Inner Ring Header':
            inner_label = v['properties']['value']
        elif v['properties']['scope'] == 'output' and v['properties']['name'] == 'Outer Ring Header':
            outer_label = v['properties']['value']
    for r in tile_data['table_rows']:
        data.append(r['column_data'])
    tile.generate_tile(data, inner_label, outer_label)
    return tile.mod


def get_markdown_tile(tile_data):
    tile = MarkdownTile()
    data = []
    for r in tile_data['table_rows']:
        data.append(r['column_data']['item'])
    tile.generate_tile(data)
    return tile.mod


def get_tile_data(sxo, req):
    wf = sxo.run_tile_wf(req['tile_id'])
    mod_type = ''
    modules = sxo.get_tile_modules()
    for m in modules:
        if m[5] == req['tile_id']:
            mod_type = m[1]
    if mod_type == 'metric_group':
        return get_metric_tile(wf)
    elif mod_type == 'markdown':
        return get_markdown_tile(wf)
    elif 'bar_chart' in mod_type:
        return get_bar_graph_tile(wf)
    elif  mod_type == 'line_chart':
        return get_line_chart_tile(wf)
    elif mod_type == 'donut_graph':
        return get_donut_tile(wf)
    else:
        return jsonify_data({})


@dashboard_api.route('/tiles', methods=['POST'])
def tiles():
    try:
        auth = get_jwt()
        sxo = SXO(auth)
        return jsonify_data(get_tile_modules(sxo))
    except Exception as e:
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

