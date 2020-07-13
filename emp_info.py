#実習課題2
#自動販売機

# coding:utf-8

#Flask,テンプレート,リクエスト読み込み
import os
from flask import Flask, render_template, request, redirect, url_for
#ファイル名をチェックする関数
from werkzeug.utils import secure_filename

#DBを使う
import mysql.connector
from mysql.connector import errorcode

#画像処理
from PIL import Image

#ランダムな文字列生成
import random, string

import re
# ひらがなの抽出
#hiragana = re.findall("[ぁ-ん]", txt)
# カタカナの抽出
#katakana = re.findall("[ァ-ン]", txt)
# 漢字の抽出
#kanji = re.findall("[一-龥]", txt)

#自分をappという名称でインスタンス化
app = Flask(__name__)

#データベースの情報
host = 'localhost' # データベースのホスト名又はIPアドレス
username = 'root'  # MySQLのユーザ名
passwd   = 'Hito05hito'    # MySQLのパスワード
dbname   = 'my_database'    # データベース名

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

#画像IDの生成（ランダム文字列）
def make_image_id(n):
   random_char = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   image_id = ''.join(random_char)
   return image_id

#DBの操作
def connect_db():
    cnx = mysql.connector.connect(host=host, user=username, password=passwd, database=dbname)
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

#クエリを実行する関数

#def can_add_emp():


#insert判定
#def can_add_department(image, name, price, stock):
#    return True, ""

#delete判定
#def can_delete():
#    return True, ""


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

#社員検索
@app.route('/emp_search', methods=['GET'])
def emp_search():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT emp_id, name FROM emp;'
        cursor.execute(query)

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_search.html",emp=emp)

#社員検索結果
@app.route('/emp_search_result', methods=['POST'])
def emp_search_result():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT emp_id, name FROM emp;'
        cursor.execute(query)

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_search_result.html",emp=emp)

#社員情報削除
@app.route('/emp_delete', methods=['GET','POST'])
def emp_delete():
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

#社員情報編集
@app.route('/emp_edit', methods=['GET','POST'])
def emp_edit():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT emp.emp_id, emp.name, emp.age, emp.gender, image.image, emp.postal_code, emp.pref, emp.address, department.department, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id;'
        cursor.execute(query)

        #update

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_edit.html")

#社員情報編集結果
@app.route('/emp_edit_result', methods=['GET','POST'])
def emp_edit_result():
    return render_template("emp_edit_result.html")

#社員情報追加
@app.route('/emp_add', methods=['GET','POST'])
def emp_add():
    emp_id = request.form.get("emp_id","")
    name = request.form.get("name","")
    age = request.form.get("age","")
    image = request.files.get("new_img","")
    postal_code = request.form.get("name","")
    pref = request.form.get("pref","")
    address = request.form.get("address","")
    department = request.form.get("department","")
    join_date = request.form.get("join_date","")
    leave_date = request.form.get("aleave_date","")

    message = ""
    can_add_emp = ""

    try:
        cnx, cursor = connect_db()

        image_path = save_image(image)
        image_id = make_image_id(8)

        #それぞれのテーブルにinsert
        add_image = "INSERT INTO image (image_id, image) VALUES({}, {});".format(image_id, image_path)
        cursor.execute(add_image)

        add_image = "INSERT INTO image (image_id, image) VALUES({}, {});".format(image_id, image_path)
        cursor.execute(add_image)
        
        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    
    return render_template("emp_add.html",image_path=image_path)

#社員データ追加結果
@app.route('/emp_add_result', methods=['GET','POST'])
def emp_add_result():
    return render_template("emp_edit_result.html")

###################
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
    department = request.form.get("department","")
    
    try:
        cnx, cursor = connect_db()

        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        add_department = "INSERT INTO department (department) VALUES({});".format(department)
        cursor.execute(add_department)
        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return render_template("de_edit.html")

#部署データ編集
@app.route('/de_edit', methods=['GET','POST'])
def de_edit():
    department_id = request.form.get("department_id","")
    department = request.form.get("department","")
    
    if "de_setting" in request.form.keys():
        try:
            cnx, cursor = connect_db()
    
            query = 'SELECT department_id, department FROM department where department_id = {};'.format(department_id)
            cursor.execute(query)
    
            edit_department = " department (department) VALUES({});".format(department)
            cursor.execute(edit_department)
            cnx.commit()
    
        except mysql.connector.Error as err:
            printError(err)
        else:
            cnx.close()

    return render_template("de_edit.html")

#部署データ編集結果
@app.route('/de_edit_result', methods=['GET','POST'])
def de_edit_result():
    return render_template("de_edit_result.html")

#部署情報削除
@app.route('/de_delete', methods=['GET','POST'])
def de_delete():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        departments = get_department_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return render_template("de_info.html")

#部署データ削除結果
@app.route('/de_delete_result', methods=['GET','POST'])
def de_delete_result():
    return render_template("de_delete_result.html")