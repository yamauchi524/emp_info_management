#実習課題2
#自動販売機

# coding:utf-8

#Flask,テンプレート,リクエスト読み込み
import os
from flask import Flask, render_template, request, flash, redirect, url_for, session
#ファイル名をチェックする関数
from werkzeug.utils import secure_filename

#DBを使う
import mysql.connector
from mysql.connector import errorcode

#画像処理
from PIL import Image

import re
# ひらがなの抽出
#hiragana = re.findall("[ぁ-ん]", txt)
# カタカナの抽出
#katakana = re.findall("[ァ-ン]", txt)
# 漢字の抽出
#kanji = re.findall("[一-龥]", txt)

import random, string

#自分をappという名称でインスタンス化
app = Flask(__name__)
app.secret_key = 'emp_info'

#データベースの情報
host = 'localhost' # データベースのホスト名又はIPアドレス
username = 'root'  # MySQLのユーザ名
passwd   = 'Hito05hito'    # MySQLのパスワード
dbname   = 'my_database'    # データベース名
buffered = True

#アップロード画像の保存場所
UPLOAD_FOLDER = './static/'
#アップロードされる拡張子の制限
#ALLOWED_EXTENSIONS = set(['png','jpeg','jpg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#画像の保存
def save_image(image):
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    image_path = './static/' + filename
    return image_path

#ランダムに画像IDを生成
def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

#DBの操作
def connect_db():
    cnx = mysql.connector.connect(host=host, user=username, password=passwd, database=dbname, buffered=buffered)
    cursor = cnx.cursor()
    return cnx, cursor

#DBのエラー文
def printError(err):
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("ユーザ名かパスワードに問題があります。")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("データベースが存在しません。")
    else:
        print(err)

#社員情報の取得
def get_emp_info(cursor):
    emp = []
    for (emp_id, name, age, gender, image, postal_code, pref, address, department, join_date, leave_date) in cursor:
        data = {"emp_id":emp_id, "name":name, "age":age, "gender":gender, "image":image, "postal_code":postal_code, "pref":pref, "address":address, "department":department, "join_date":join_date, "leave_date":leave_date}
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

#リクエスト情報の取得
def get_request():
    emp_id = request.form.get("emp_id","")
    name = request.form.get("name","")
    age = request.form.get("age","")
    gender = request.form.get("gender","")
    image = request.files.get("new_img","")
    postal_code = request.form.get("name","")
    pref = request.form.get("pref","")
    address = request.form.get("address","")
    department_id = request.form.get("department_id","")
    join_date = request.form.get("join_date","")
    leave_date = request.form.get("leave_date","")

    return emp_id, name, age, gender, image, postal_code, pref, address, department_id, join_date, leave_date


#編集できたか判定（社員）
def can_edit_emp(emp_id, name, age, gender, image, postal_code, pref, address, department):
    if emp_id == "" or name == "" or age == "" or gender == "" or image == "" or postal_code == "" or pref == "" or address == "" or department == "":
        return False
    return True

#編集できたか判定（部署）
def can_edit_department(department):
    if department == "":
        #return False, 1
        return False
    if re.fullmatch('[a-zA-Z0-9]+',department):
        #return False, 1
        return False
    #return True, 2
    return True

#クエリを実行する関数をかく
#def add_emp():

#def edit_emp():

#def delete_emp():

#def add_department():

#def edit_department():

#def delete_department():

#社員情報一覧
@app.route('/emp_info', methods=['GET','POST'])
def emp_info():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id;'
        cursor.execute(query)

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_info.html", emp=emp)

#社員情報追加
@app.route('/emp_add', methods=['GET','POST'])
def emp_add():
    emp_id, name, age, gender, image, postal_code, pref, address, department_id, join_date, leave_date = get_request()
    can_add = ""

    try:
        cnx, cursor = connect_db()

        emp_query = 'SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id;'
        cursor.execute(emp_query)

        department_query = 'SELECT department_id, department FROM department;'
        cursor.execute(department_query)
        departments = get_department_info(cursor)
        
        if "emp_setting" in request.form.keys():
            can_add = can_edit_emp(emp_id, name, age, gender, image, postal_code, pref, address, department_id)

            if can_add:
                image_path = save_image(image)
                image_id = randomname(8)

                add_image = "INSERT INTO image (image_id, image) VALUE('{}', '{}');".format(image_id, image_path)
                cursor.execute(add_image)
                
                add_emp = "INSERT INTO emp (emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date) VALUES('{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}');".format(emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date)
                cursor.execute(add_emp)

                cnx.commit()

                flash("データの更新に成功しました","success")
                return render_template("emp_result.html")

            else:
                flash("データの更新に失敗しました","failed")
                return render_template("emp_result.html")

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    
    return render_template("emp_edit.html", departments=departments)

#社員情報編集
@app.route('/emp_edit', methods=['GET','POST'])
def emp_edit():
    emp_id = request.form.get("emp_edit","")

    try:
        cnx, cursor = connect_db()

        query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE emp.emp_id = '{}';".format(emp_id)
        cursor.execute(query)

        emp = get_emp_info(cursor)

        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)
        departments = get_department_info(cursor)

        #if "emp_setting"
        

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_edit.html", emp=emp, departments=departments)

#社員情報削除
@app.route('/emp_delete', methods=['GET','POST'])
def emp_delete():
    emp_id = request.form.get("emp_delete","")

    try:
        cnx, cursor = connect_db()

        query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE = emp.emp_id = '{}';".format(emp_id)
        cursor.execute(query)

        emp = get_emp_info(cursor)

        #if "emp_delete"

    except mysql.connector.Error as err:
        printError(err)
        flash("データの削除に失敗しました","failed")
    else:
        cnx.close()
    
    flash("データの削除に成功しました","success")
    return redirect(url_for('emp_info'))
    #return render_template("emp_info.html", emp=emp)

#CSV出力
#@app.route('/csv', methods=['GET','POST'])
#def output_to_csv():
#    return render_template

#社員検索
@app.route('/emp_search', methods=['GET','POST'])
def emp_search():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)
        departments = get_department_info(cursor)

        #if "emp_search" in request.form.keys():

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_search.html", departments=departments)

#社員検索結果
@app.route('/emp_search_result', methods=['GET','POST'])
def emp_search_result():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id;'
        cursor.execute(query)

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_search_result.html",emp=emp)


###########################
#部署データ一覧
@app.route('/de_info', methods=['GET','POST'])
def de_info():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        departments = get_department_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("de_info.html",departments=departments)

#部署データ新規追加
@app.route('/de_add', methods=['GET','POST'])
def de_add():
    department = request.form.get("new_department","")
    can_add = ""

    try:
        cnx, cursor = connect_db()
        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        if "de_setting" in request.form.keys():
            can_add = can_edit_department(department)

            if can_add:
                add_department = "INSERT INTO department(department) VALUES('{}');".format(department)
                cursor.execute(add_department)
                cnx.commit()

                flash("データの更新に成功しました","success")
                return render_template("de_result.html")

            else:
                flash("データの更新に失敗しました","failed")
                return render_template("de_result.html")

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return render_template("de_edit.html")

#部署データ編集（UnboundlocalErrorが出るよ）
@app.route('/de_edit', methods=['GET','POST'])
def de_edit():
    department_id = request.form.get("de_edit","")
    new_department = request.form.get("new_department","")
    can_edit = ""
    
    try:
        cnx, cursor = connect_db()
        query = 'SELECT department_id, department FROM department WHERE department_id = {};'.format(department_id)
        cursor.execute(query)
        departments = get_department_info(cursor)
        
        if "de_setting" in request.form.keys():
            can_edit = can_edit_department(new_department)
            #どこかでエラー出てる？

            if can_edit:
                update_department = "UPDATE department SET department = '{}' WHERE department_id = {};".format(new_department, department_id)
                cursor.execute(update_department)
                cnx.commit()

                flash("データの更新に成功しました","success")
                return render_template("de_result.html")
                
            else:
                flash("データの更新に失敗しました","failed")
                return render_template("de_result.html")

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return render_template("de_edit.html", departments=departments)

#部署データ編集結果
#@app.route('/de_result', methods=['GET','POST'])
#def de_result():
#    return render_template("de_result.html")

#@app.route('/de_result_failed', methods=['GET','POST'])
#def de_result_failed():
#    return render_template("de_result_failed.html")

#部署情報削除
@app.route('/de_delete', methods=['GET','POST'])
def de_delete():
    department_id = request.form.get("de_delete","")
    
    try:
        cnx, cursor = connect_db()
        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        delete_department = 'DELETE FROM department WHERE department_id = {};'.format(department_id)
        cursor.execute(delete_department)
        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
        flash("データを削除することができませんでした。","failed")
    else:
        cnx.close()

    flash("データの削除に成功しました","success")
    return redirect(url_for('de_info'))