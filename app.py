#実習課題3
#社員情報管理ツール
#coding:utf-8

import os
from flask import Flask, render_template, request, flash, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from io import StringIO

import re
import random, string

import mysql.connector
from mysql.connector import errorcode
import model.database as db
import model.validation as valid

app = Flask(__name__)
app.secret_key = 'emp_info'

#画像フォルダ
UPLOAD_FOLDER = './static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#画像の保存
def save_image(image):
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    # image_path = './static/' + filename
    # return image_path
    return filename

#ランダムに画像IDを生成
def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

#社員追加のリクエスト情報の取得
def get_add_request():
    emp_id = request.form.get("emp_id","")
    name = request.form.get("name","")
    age = request.form.get("age","")
    gender = request.form.get("gender","")
    image = request.files.get("image","")
    postal_code = request.form.get("postal_code","")
    pref = request.form.get("pref","")
    address = request.form.get("address","")
    department_id = request.form.get("department_id","")
    join_date = request.form.get("join_date","")
    leave_date = request.form.get("leave_date","")

    return emp_id, name, age, gender, image, postal_code, pref, address, department_id, join_date, leave_date

#社員編集のリクエスト情報の取得
def get_edit_request():
    emp_id = request.form.get("emp_id","")
    name = request.form.get("name","")
    age = request.form.get("age","")
    gender = request.form.get("gender","")
    image_id = request.form.get("image_id","")
    image = request.files.get("image","")
    # edit_image = request.files.get("edit_image","")
    postal_code = request.form.get("postal_code","")
    pref = request.form.get("pref","")
    address = request.form.get("address","")
    department_id = request.form.get("department_id","")
    join_date = request.form.get("join_date","")
    leave_date = request.form.get("leave_date","")

    return emp_id, name, age, gender, image_id, image, postal_code, pref, address, department_id, join_date, leave_date

#検索情報の取得
def get_search_info():
    search_department = request.form.get("search_department","")
    search_emp_id = request.form.get("search_emp_id","")
    search_name = request.form.get("search_name","")
    return search_department, search_emp_id, search_name

#社員情報一覧
@app.route('/emp_info', methods=['GET','POST'])
def emp_info():
    emp = db.show_emp_info()
    return render_template("emp_info.html", emp=emp)

#社員情報追加
@app.route('/emp_add', methods=['GET','POST'])
def emp_add():
    departments = db.show_de_info()    
    return render_template("emp_edit.html", departments=departments)

#社員情報追加処理
@app.route('/save_emp_add', methods=['GET','POST'])
def save_emp_add():
    emp_id, name, age, gender, image, postal_code, pref, address, department_id, join_date, leave_date = get_add_request()
    can_add, message = valid.can_add_emp(emp_id, name, age, gender, image, postal_code, pref, address)

    if can_add:
        filename = save_image(image)
        image_id = randomname(8)

        db.save_add_emp_info(emp_id, name, age, gender, image, image_id, filename, postal_code, pref, address, department_id, join_date, leave_date)

    else:
        flash("{}".format(message),"failed")
        return render_template("emp_result.html")

    flash("{}".format(message),"success")
    return render_template("emp_result.html")

#社員情報編集
@app.route('/emp_edit', methods=['GET','POST'])
def emp_edit():
    emp_id = request.form.get("emp_edit","")
    emp, departments = db.show_emp_edit(emp_id)
    return render_template("emp_edit.html", emp=emp, departments=departments)

#社員情報編集処理
@app.route('/save_emp_edit', methods=['GET','POST'])
def save_emp_edit():
    emp_id, name, age, gender, image_id, image, postal_code, pref, address, department_id, join_date, leave_date = get_edit_request()
    can_edit, message = valid.can_edit_info(emp_id, name, age, gender, image_id, image, postal_code, pref, address, department_id, join_date, leave_date)
    
    if can_edit:
        filename = save_image(image)
        db.save_edit_emp_info(name, age, gender, filename, postal_code, pref, address, department_id, join_date, leave_date, emp_id)

    else:
        flash("{}".format(message),"failed")
        return render_template("emp_result.html")

    flash("{}".format(message),"success")
    return render_template("emp_result.html")

#社員情報削除
@app.route('/emp_delete', methods=['GET','POST'])
def emp_delete():
    emp_id = request.form.get("emp_delete","")
    db.execute_emp_delete(emp_id)
    
    flash("データの削除に成功しました","success")
    return render_template("emp_result.html")

#CSV出力
@app.route('/csv', methods=['GET','POST'])
def output_to_csv():
    csv = db.make_csv()
    response = make_response(csv)
    response.headers['Content-Disposition'] = 'attachment; filename = emp_information.csv'
    return response

#社員検索
@app.route('/emp_search', methods=['GET','POST'])
def emp_search():
    departments = db.show_de_info()
    return render_template("emp_search.html", departments=departments)

#社員検索結果
@app.route('/emp_search_result', methods=['GET','POST'])
def emp_search_result():
    search_department, search_emp_id, search_name = get_search_info()
    emp = db.search_emp(search_department, search_emp_id, search_name)
    return render_template("emp_search_result.html",emp=emp)

###########################
#部署データ一覧
@app.route('/de_info', methods=['GET','POST'])
def de_info():
    departments = db.show_de_info()
    return render_template("de_info.html",departments=departments)

#部署データ新規追加
@app.route('/de_add', methods=['GET','POST'])
def de_add():
    return render_template("de_edit.html")

#部署データ追加処理
@app.route('/save_de_add', methods=['POST'])
def save_de_add():
    department = request.form.get("new_department","")
    can_add, message = valid.can_edit_department(department)

    if can_add:
        db.save_add_de_info(department)

    else:
        flash("{}".format(message),"failed")
        return render_template("de_result.html") 

    flash("{}".format(message),"success")
    return render_template("de_result.html")

#部署データ編集
@app.route('/de_edit', methods=['GET','POST'])
def de_edit():
    department_id = request.form.get("de_edit","")
    departments = db.show_de_edit(department_id)
    return render_template("de_edit.html", departments=departments)

#部署データ編集処理
@app.route('/save_de_edit', methods=['GET','POST'])
def save_de_edit():
    department_id = request.form.get("department_id","")
    new_department = request.form.get("new_department","")
    can_edit, message = valid.can_edit_department(new_department)

    if can_edit:
        db.save_edit_de_info(new_department, department_id)

    else:
        flash("{}".format(message),"failed")
        return render_template("de_result.html")

    flash("{}".format(message),"success")
    return render_template("de_result.html")

#部署情報削除
@app.route('/de_delete', methods=['GET','POST'])
def de_delete():
    department_id = request.form.get("de_delete","")
    db.execute_de_delete(department_id)

    flash("データの削除に成功しました","success")
    return render_template("de_result.html")