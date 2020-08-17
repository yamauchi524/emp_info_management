#Flask,テンプレート,リクエスト読み込み
import os
from flask import Flask, render_template, request, flash, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from io import StringIO
import datetime
import re
# import random, string

import mysql.connector
from mysql.connector import errorcode
from model.const import DB
import model.validation as valid

app = Flask(__name__)

# DB接続
def get_connection():
    cnx = mysql.connector.connect(host=DB["DB_HOST"], user=DB["DB_USER_NAME"], password=DB["DB_PASSWORD"], database=DB["DB_NAME"], buffered=DB["DB_BUFFERED"])
    cursor = cnx.cursor()
    return cnx, cursor

def printError(err):
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("ユーザ名かパスワードに問題があります。")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("データベースが存在しません。")
    else:
        print(err)

# #画像の保存
# def save_image(image):
#     filename = secure_filename(image.filename)
#     image.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
#     # image_path = './static/' + filename
#     # return image_path
#     return filename

# #ランダムに画像IDを生成
# def randomname(n):
#    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
#    return ''.join(randlst)

#社員情報の取得
def get_emp_info(cursor):
    emp = []
    for (emp_id, name, age, gender, image, postal_code, pref, address, department, join_date, leave_date) in cursor:
        data = {"emp_id":emp_id, "name":name, "age":age, "gender":gender, "image":image, "postal_code":postal_code, "pref":pref, "address":address, "department":department, "join_date":join_date, "leave_date":leave_date}
        emp.append(data)
    return emp

#編集時の社員情報の取得
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

# #画像情報の取得
# def get_image_info(cursor):
#     images = []
#     for (image_id, image) in cursor:
#         img = {"image_id":image_id,"image":image}
#         images.append(img)
#     return images

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
def show_emp_info():
    try:
        cnx, cursor = get_connection()

        emp_query = execute_emp_query()
        cursor.execute(emp_query)

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return emp

#社員情報追加
def save_add_emp_info(emp_id, name, age, gender, image, image_id, filename, postal_code, pref, address, department_id, join_date, leave_date):
    try:
        cnx, cursor = get_connection()

        add_image = "INSERT INTO image (image_id, image, emp_id) VALUE('{}', '{}', '{}');".format(image_id, filename, emp_id)
        cursor.execute(add_image)
                
        add_emp = "INSERT INTO emp (emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date) VALUES('{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}');".format(emp_id, name, age, gender, image_id, postal_code, pref, address, department_id, join_date, leave_date)
        cursor.execute(add_emp)

        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

#社員情報編集画面
def show_emp_edit(emp_id):
    try:
        cnx, cursor = get_connection()

        query = "SELECT emp.emp_id, emp.name, emp.age, emp.gender, emp.image_id, image.image, emp.postal_code, emp.pref, emp.address, department.department, department.department_id, emp.join_date, emp.leave_date FROM emp LEFT JOIN image ON emp.image_id = image.image_id LEFT JOIN department ON emp.department_id = department.department_id WHERE emp.emp_id = '{}';".format(emp_id)
        cursor.execute(query)

        emp = get_edit_emp_info(cursor)

        department_query = execute_department_query()
        cursor.execute(department_query)
        departments = get_department_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return emp, departments

# 社員情報編集処理
def save_edit_emp_info(name, age, gender, filename, postal_code, pref, address, department_id, join_date, leave_date, emp_id):
    try:
        cnx, cursor = get_connection()

        update_emp_info = "UPDATE emp LEFT JOIN image ON emp.image_id = image.image_id SET emp.name = '{}', emp.age = {}, emp.gender = '{}', image.image = '{}', emp.postal_code = '{}', emp.pref = '{}', emp.address = '{}', emp.department_id = {}, emp.join_date = '{}', emp.leave_date = '{}' WHERE emp.emp_id = '{}';".format(name, age, gender, filename, postal_code, pref, address, department_id, join_date, leave_date, emp_id)
        cursor.execute(update_emp_info)

        cnx.commit()
        
    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

#社員情報の削除
def execute_emp_delete(emp_id):
    try:
        cnx, cursor = get_connection()
        emp_query = execute_emp_query()
        cursor.execute(emp_query)

        delete_emp = "DELETE FROM emp WHERE emp_id = '{}';".format(emp_id)
        cursor.execute(delete_emp)

        delete_image = "DELETE FROM image WHERE emp_id = '{}';".format(emp_id)
        cursor.execute(delete_image)
        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

#部署情報一覧
def show_de_info():
    try:
        cnx, cursor = get_connection()

        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        departments = get_department_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return departments


def show_de_edit(department_id):
    try:
        cnx, cursor = get_connection()
        query = 'SELECT department_id, department FROM department WHERE department_id = {};'.format(department_id)
        cursor.execute(query)
        departments = get_department_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return departments


#部署情報の削除
def execute_de_delete(department_id):
    try:
        cnx, cursor = get_connection()
        query = 'SELECT department_id, department FROM department;'
        cursor.execute(query)

        delete_department = 'DELETE FROM department WHERE department_id = {};'.format(department_id)
        cursor.execute(delete_department)
        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

#csv
def make_csv():
    try:
        cnx, cursor = get_connection()
        csv = get_csv(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

    return csv

#検索
def search_emp(search_department, search_emp_id, search_name):
    try:
        cnx, cursor = get_connection()

        search_query = execute_search_query(search_department, search_emp_id, search_name)
        cursor.execute(search_query)

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    
    return emp

#部署情報追加
def save_add_de_info(department):
    try:
        cnx, cursor = get_connection()

        add_department = "INSERT INTO department(department) VALUES('{}');".format(department)
        cursor.execute(add_department)
        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()

def save_edit_de_info(new_department, department_id):
    try:
        cnx, cursor = get_connection()
        update_department = "UPDATE department SET department = '{}' WHERE department_id = {};".format(new_department, department_id)
        cursor.execute(update_department)
        cnx.commit()

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()