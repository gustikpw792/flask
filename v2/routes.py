from flask import Blueprint, jsonify

# Buat blueprint untuk v2
bp_v2 = Blueprint('v2', __name__, url_prefix='/api/v2')

@bp_v2.route('/users', methods=['GET'])
def get_users():
    return jsonify({
        'version': 'v2',
        'users': [
            {'id': 1, 'name': 'User from v2'},
            {'id': 2, 'name': 'Another user v2'}
        ]
    })