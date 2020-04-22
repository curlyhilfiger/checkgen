from functools import wraps

from flask import request, jsonify

from app.services import printer_service



def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if 'api_key' not in request.args:
            return jsonify({'error': 'Ошибка авторизации'}), 401
           
        api_key = request.args['api_key']  
        
        printer = printer_service.get_printer(api_key)

        return f(printer, *args, **kwargs)

    return decorated


def id_required(f):
    @wraps
    def decorated(*args, **kwargs):

        if 'id' not in request.args:
            return jsonify({'error':'не указан id'})

        id = request.args['id']

        return f(id, *args, **kwargs)
    
    return decorated

