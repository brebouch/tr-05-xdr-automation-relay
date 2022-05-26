from flask import Blueprint
from api.sxo import SXO
import api.securex as securex

from api.utils import get_jwt, jsonify_data, get_instance

health_api = Blueprint('health', __name__)

def check_logo(auth):
    instance = get_instance()
    sec = securex.SecureX(auth['API_CLIENT'], auth['API_SECRET'])
    mod_instance = sec.get_module_instance(instance)
    mod_type = sec.get_module_type(mod_instance['module_type_id'])
    encoded = sec.encode_img(mod_instance['settings']['custom_ICON'])
    if encoded != mod_type['logo']:
        for c in range(len(mod_type['configuration_spec'])):
            if mod_type['configuration_spec'][c]['key'] == 'custom_ICON':
                del mod_type['configuration_spec'][c]
                break
        mod_type['title'] = mod_instance['name']
        mod_type['logo'] = encoded
        new_mod_type = sec.create_module_type(mod_type)
        print('hi')
        
        
def check_config_spec(current_config, workflows):
    cfg = [current_config[0]]
    for w in workflows:
        cfg.append({'value': w['name'], 'label': w['name']})
    return cfg


@health_api.route('/health', methods=['POST'])
def health():
    auth = get_jwt()
    try:
        sxo = SXO(auth)
        deliberate = sxo.get_workflow_by_category('deliberate')
        observe = sxo.get_workflow_by_category('observe')
        instance = get_instance()
        sec = securex.SecureX(auth['API_CLIENT'], auth['API_SECRET'])
        mod_instance = sec.get_module_instance(instance)
        mod_type = sec.get_module_type(mod_instance['module_type_id'])
        for spec in mod_type['configuration_spec']:
            if spec['key'] == 'custom_DELIBERATE_WORKFLOW':
                spec['options'] = check_config_spec(spec['options'], deliberate)
            if spec['key'] == 'custom_OBSERVE_WORKFLOW':
                spec['options'] = check_config_spec(spec['options'], observe)
            if spec['key'] == 'custom_TILE_TABLE':
                spec['options'] = sxo.get_tile_table_types()
        mod_type.pop('org_id')
        mod_type.pop('id')
        mod_type.pop('record')
        mod_type.pop('user_id')
        mod_type.pop('client_id')
        mod_type.pop('visibility')
        mod_type.pop('created_at')
        try:
            mod_type.pop('updated_at')
        except:
            pass
        sec.update_module_type(mod_instance['module_type_id'], mod_type)
    except:
        pass
    #sxo.create_input_config(sxo.refer_id, 'ip', 'sxo test object')
    #sxo.run_workflow(sxo.refer_id)
    return jsonify_data({'status': 'ok'})
