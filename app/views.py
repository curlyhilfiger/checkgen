from flask import jsonify, request, render_template, send_file

from app.models import Printer, Check
from app.services import pdf_service
from app.tasks.background_generate import generate

from app import app
from app import db
from app import q

import os
import pypandoc


@app.route('/create_checks', methods=['POST'])
def create_checks():
    if request.is_json:
        data = request.get_json()

        if is_created(data['id']):
            return jsonify({'error': 'Для данного заказа уже созданы чеки'}), 400

        printers = Printer.query.filter_by(point_id=data['point_id']).all()
        
        if printers:
            
            job = q.enqueue(generate, data=data)
            print(f'Task ({job.id}) added to queue at {job.enqueued_at}')


            return jsonify({'ok':'Чеки успешно созданы'})

        return jsonify({'msg':'Для данной точки не настроено ни одного принтера'})

    return jsonify({'msg': 'no json recivied'})


@app.route('/new_checks/<api_key>', methods=["GET"])
def new_checks(api_key):

    printer = Printer.query.filter_by(api_key=api_key).first()

    if printer:
        checks = Check.query.filter_by(printer_id=printer.id, status='rendered').all()

        print(checks)

        output = []

        for check in checks:

            check_data = {}
            check_data['id'] = check.id
            output.append(check_data)

        return jsonify({'msg': output})
    
    return jsonify({'error': 'Ошибка авторизации'}), 401


@app.route('/check/<api_key>/<id>')
def check(api_key, id):

    printer = Printer.query.filter_by(api_key=api_key).first()

    if printer:

        check = Check.query.filter_by(id=id, printer=printer).first()

        if check:

            filename = check.pdf_file

            check.status = 'printed'
            db.session.commit()

            
            return send_file(
                filename_or_fp=filename,
                mimetype='application/pdf',
                as_attachment=True
            )
        
        else:
            return jsonify({'error':'Данного чека не существует или файл не создан'}), 400

    else:
        return jsonify({'error': 'Ошибка авторизации'}), 401
    



def background_check(data, printers):
    
    for printer in printers:

        pdf_file = pdf_service.pdf(data, str(printer.check_type))

        print(pdf_file)

        check = Check(
            order_id=data['id'],
            printer=printer,
            check_type=printer.check_type,
            order=data,
            status='rendered',
            pdf_file=pdf_file
        )
        db.session.add(check)
    
    db.session.commit()
    print('checks added')


def is_created(order_id):

    check = Check.query.filter_by(order_id=order_id).first()

    if not check:
        return False

    return True