#実習課題3
#社員情報管理ツール
#coding:utf-8

#Flask,テンプレート,リクエスト読み込み
import os
from flask import Flask, render_template, request, flash, redirect, url_for, make_response
#ファイル名をチェックする
from werkzeug.utils import secure_filename
from io import StringIO

import re
import random, string

#DBを使う
import mysql.connector
from mysql.connector import errorcode
import model.database as db
# import model.validation as valid

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

#DBの操作
# def connect_db():
#     cnx = mysql.connector.connect(host=host, user=username, password=passwd, database=dbname, buffered=buffered)
#     cursor = cnx.cursor()
#     return cnx, cursor

#DBのエラー文
def printError(err):
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("ユーザ名かパスワードに問題があります。")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("データベースが存在しません。")
    else:
        print(err)

#社員情報の取得
# def get_emp_info(cursor):
#     emp = []
#     for (emp_id, name, age, gender, image, postal_code, pref, address, department, join_date, leave_date) in cursor:
#         data = {"emp_id":emp_id, "name":name, "age":age, "gender":gender, "image":image, "postal_code":postal_code, "pref":pref, "address":address, "department":department, "join_date":join_date, "leave_date":leave_date}
#         emp.append(data)
#     return emp

#編集する社員情報の取得
def get_edit_emp_info(cursor):
    emp = []
    for (emp_id, name, age, gender, image_id, image, postal_code, pref, address, department, department_id, join_date, leave_date) in cursor:
        data = {"emp_id":emp_id, "name":name, "age":age, "gender":gender, "image_id":image, "image":image, "postal_code":postal_code, "pref":pref, "address":address, "department":department, "department_id":department_id, "join_date":join_date, "leave_date":leave_date}
        emp.append(data)
    return emp

#部署情報の取得
def get_department_info(cursor):
    departments = []
    for (department_id, department) in cursor:
        belongs = {"department_id":department_id,"department":department}
        departments.append(belongs)
    return departments

#画像情報の取得
def get_image_info(cursor):
    images = []
    for (image_id, image) in cursor:
        img = {"image_id":image_id,"image":image}
        images.append(img)
    return images

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

#追加できるかの判定（社員）
def can_add_emp(emp_id, name, age, gender, image, postal_code, pref, address):
    if emp_id == "" or name == "" or age == "" or gender == "" or image == "" or postal_code == "" or address == "":
        return False, "入力情報に不備があります。"
    elif not re.match('^[0-9]{3}-[0-9]{4}$', postal_code):
        return False, "郵便番号を正しい形式で入力してください。"
    elif not age.isdecimal():
        return False, "年齢は整数で入力してください。"
    else:
        return True, "データの更新に成功しました。"

#編集できるかの判定（社員）
def can_edit_info(emp_id, name, age, gender, image_id, image, postal_code, pref, address, department_id, join_date, leave_date):
    if emp_id == "" or name == "" or age == "" or gender == "" or image == "" or postal_code == "" or address == "" or join_date == "" or leave_date == "":
        return False, "入力情報に不備があります。"
    if not re.match('^emp+[0-9]{4}$', emp_id):
        return False, "社員番号の表記が違います。"
    if not age.isdecimal():
        return False, "年齢は整数で入力してください。"
    if not re.match('^[0-9]{3}-[0-9]{4}$', postal_code):
        return False, "郵便番号を正しい形式で入力してください。"
    if not re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', join_date):
        return False, "入社日を正しい形式で入力してください。"
    return True, "データの更新に成功しました。"

#編集できるかの判定（部署）
def can_edit_department(department):
    if department == "":
        #return False, 1
        return False, "入力情報に不備があります。"
    if re.fullmatch('[a-zA-Z0-9]+',department):
        #return False, 1
        return False, "入力情報に不備があります。"
    else:
        return True, "データの更新に成功しました。"

#検索情報の取得
def get_search_info():
    search_department = request.form.get("search_department","")
    search_emp_id = request.form.get("search_emp_id","")
    search_name = request.form.get("search_name","")
    return search_department, search_emp_id, search_name

#検索の入力情報でどのクエリを実行するか決定
def execute_search_query(search_department, search_emp_id, search_name):
    if search_department == "" and search_emp_id == "" and search_name == "":
        search_query = 'SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id;'
    if search_department != "" and search_emp_id == "" and search_name == "": #部署だけ
        search_query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE department.department = '{}';".format(search_department) 
    if search_department == "" and search_emp_id != "" and search_name == "": #IDだけ
        search_query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE emp.emp_id = '{}';".format(search_emp_id)
    if search_department == "" and search_emp_id == "" and search_name != "": #名前だけ
        search_query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE emp.name LIKE '%{}%';".format(search_name)
    if search_department != "" and search_emp_id != "" and search_name == "": #部署&ID
        search_query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE department.department = '{}' AND emp.emp_id = '{}';".format(search_department, search_emp_id)
    if search_department != "" and search_emp_id == "" and search_name != "": #部署&名前
        search_query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE department.department = '{}' AND emp.name LIKE '%{}%';".format(search_department, search_name)
    if search_department == "" and search_emp_id != "" and search_name != "": #ID&名前
        search_query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE emp.emp_id = '{}' AND emp.name LIKE '%{}%';".format(search_emp_id, search_name)
    if search_department != "" and search_emp_id != "" and search_name != "": #全部
        search_query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE department.department = '{}' AND emp.emp_id = '{}' AND emp.name LIKE '%{}%';".format(search_department, search_emp_id, search_name)
    return search_query

#csv出力
def get_csv(cursor):
    csv = "社員ID, 氏名, 年齢, 性別, 画像ID, 郵便番号, 都道府県, 住所, 部署ID, 入社日, 退社日, 登録日, 更新日 \n"
    csv_query = 'SELECT emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date, register_date, update_date FROM emp;'
    cursor.execute(csv_query)
    for (emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date, register_date, update_date) in cursor:
        csv += "'{}','{}',{},'{}','{}','{}','{}','{}',{},'{}','{}','{}','{}' \n".format(emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date, register_date, update_date)
    return csv

#クエリ実行（社員）
def execute_emp_query():
    emp_query = 'SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id;'
    return emp_query

#クエリ実行（部署）
def execute_department_query():
    department_query = 'SELECT department_id, department FROM department;'
    return department_query

#社員情報一覧
@app.route('/emp_info', methods=['GET','POST'])
def emp_info():
    emp = db.show_emp_info()
    return render_template("emp_info.html", emp=emp)

#社員情報追加
@app.route('/emp_add', methods=['GET','POST'])
def emp_add():
    emp_id, name, age, gender, image, postal_code, pref, address, department_id, join_date, leave_date = get_add_request()
    can_add = ""

    try:
        cnx, cursor = db.get_connection()

        department_query = execute_department_query()
        cursor.execute(department_query)
        departments = get_department_info(cursor)
        
        if "emp_setting" in request.form.keys():
            can_add, message = can_add_emp(emp_id, name, age, gender, image, postal_code, pref, address)
            
            if can_add:
                filename = save_image(image)
                image_id = randomname(8)

                add_image = "INSERT INTO image (image_id, image, emp_id) VALUE('{}', '{}', '{}');".format(image_id, filename, emp_id)
                cursor.execute(add_image)
                
                add_emp = "INSERT INTO emp (emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date) VALUES('{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}');".format(emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date)
                cursor.execute(add_emp)

                cnx.commit()

                flash("{}".format(message),"success")
                return render_template("emp_result.html")

            else:
                flash("{}".format(message),"failed")
                return render_template("emp_result.html")

    except mysql.connector.Error as err:
        printError(err)
        flash("{}".format(message),"failed")
        return render_template("emp_result.html")
    else:
        cnx.close()
    
    return render_template("emp_edit.html", departments=departments)

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
    can_edit, message = can_edit_info(emp_id, name, age, gender, image_id, image, postal_code, pref, address, department_id, join_date, leave_date)
    
    try:
        cnx, cursor = db.get_connection()

        if "emp_setting" in request.form.keys():
            if can_edit:
                filename = save_image(image)

                update_emp_info = "UPDATE emp LEFT JOIN image ON emp.image_id = image.image_id SET emp.name = '{}', emp.age = {}, emp.gender = '{}', image.image = '{}', emp.postal_code = '{}', emp.pref = '{}', emp.address = '{}', emp.department_id = {}, emp.join_date = '{}', emp.leave_date = '{}' WHERE emp.emp_id = '{}';".format(name, age, gender, filename, postal_code, pref, address, department_id, join_date, leave_date, emp_id)
                cursor.execute(update_emp_info)

                cnx.commit()

            else:
                flash("{}".format(message),"failed")
                return render_template("emp_result.html")
        
    except mysql.connector.Error as err:
        printError(err)
        flash("{}".format(message),"failed")
        return render_template("emp_result.html")

    else:
        cnx.close()
    
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
    try:
        cnx, cursor = db.get_connection()
        csv = get_csv(cursor)

        response = make_response(csv)
        response.headers['Content-Disposition'] = 'attachment; filename = emp_information.csv'

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return response

#社員検索
@app.route('/emp_search', methods=['GET','POST'])
def emp_search():
    try:
        cnx, cursor = db.get_connection()
        department_query = execute_department_query()
        cursor.execute(department_query)
        departments = get_department_info(cursor) 

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_search.html", departments=departments)

#社員検索結果
@app.route('/emp_search_result', methods=['GET','POST'])
def emp_search_result():
    search_department, search_emp_id, search_name = get_search_info()

    try:
        cnx, cursor = db.get_connection()

        search_query = execute_search_query(search_department, search_emp_id, search_name)
        cursor.execute(search_query)

        emp = db.get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
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
    department = request.form.get("new_department","")
    can_add = ""

    try:
        cnx, cursor = db.get_connection()
        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        if "de_setting" in request.form.keys():
            can_add, message = can_edit_department(department)

            if can_add:
                add_department = "INSERT INTO department(department) VALUES('{}');".format(department)
                cursor.execute(add_department)
                cnx.commit()

                flash("{}".format(message),"success")
                return render_template("de_result.html")

            else:
                flash("{}".format(message),"failed")
                return render_template("de_result.html")

    except mysql.connector.Error as err:
        printError(err)
        flash("{}".format(message),"failed")
        return render_template("de_result.html")
    else:
        cnx.close()

    return render_template("de_edit.html")

#部署データ編集
@app.route('/de_edit', methods=['GET','POST'])
def de_edit():
    department_id = request.form.get("de_edit","")
    new_department = request.form.get("new_department","")

    departments = db.show_de_edit(department_id)

    return render_template("de_edit.html", departments=departments)

#部署データ編集処理
@app.route('/save_de_edit', methods=['GET','POST'])
def save_de_edit():
    department_id = request.form.get("department_id","")
    new_department = request.form.get("new_department","")
    can_edit = ""

    try:
        cnx, cursor = db.get_connection()

        if "de_setting" in request.form.keys():
            can_edit, message = can_edit_department(new_department)

            if can_edit:
                update_department = "UPDATE department SET department = '{}' WHERE department_id = {};".format(new_department, department_id)
                cursor.execute(update_department)
                cnx.commit()
                
            else:
                flash("{}".format(message),"failed")
                return render_template("de_result.html")

    except mysql.connector.Error as err:
        printError(err)
        flash("{}".format(message),"failed")
        return render_template("de_result.html")
    else:
        cnx.close()

    flash("{}".format(message),"success")
    return render_template("de_result.html")

#部署情報削除
@app.route('/de_delete', methods=['GET','POST'])
def de_delete():
    department_id = request.form.get("de_delete","")
    db.execute_de_delete(department_id)

    flash("データの削除に成功しました","success")
    return render_template("de_result.html")