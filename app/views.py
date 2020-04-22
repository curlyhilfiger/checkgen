from flask import jsonify, request, render_template, send_file

from app.services import pdf_service, check_service, printer_service
from app.tasks.background_generate import generate
from app.utils.decorator import api_key_required
from app import app
from app import db
from app import q

import os
import pypandoc


@app.route('/create_checks', methods=['POST'])
def create_checks():

    if request.is_json:
        data = request.get_json()

        if check_service.is_created(data['order_id']):
            response = {
                'error': 'Для данного заказа уже созданы чеки'
            }
            return jsonify(response), 401

        printers = printer_service.get_printers(data['point_id'])
        if printers:

            job = q.enqueue(generate, data=data)
            print(f'Task ({job.id}) added to queue at {job.enqueued_at}')

            response = {'ok': 'Чеки успешно созданы'}
            return jsonify(response)

        response = {
            'msg': 'Для данной точки не настроено ни одного принтера'
        }
        return jsonify(response), 401

    return jsonify({'msg': 'no json recivied'})


@app.route('/new_checks', methods=['GET'])
@api_key_required
def new_checks(printer):

    checks = check_service.get_checks(printer.id)

    print(checks)

    output = []

    for check in checks:

        check_data = {}
        check_data['id'] = check.id
        output.append(check_data)

    return jsonify({'msg': output})


@app.route('/check/<id>', methods=['GET'])
@api_key_required
def check(printer, id):

    check = check_service.get_check(id, printer_id=printer.id)

    if check:

        filename = check.pdf_file

        check.status = 'printed'
        db.session.commit()

        return send_file(
            filename_or_fp=filename,
            mimetype='application/pdf',
            as_attachment=True,
        )
    else:

        response = {
            'error': 'Данного чека не существует или файл не создан'
        }
        return jsonify(response), 400
