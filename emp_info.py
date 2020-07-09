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
    for (drink_id, image, name, price, stock, status) in cursor:
        data = {"drink_id":drink_id, "image":sql_image, "name":name, "price":price, "stock":stock, "status":status}
        emp.append(data)
    return emp




#社員情報
@app.route('/emp_info', methods=['GET','POST'])
def emp_info():
    try:
        cnx, cursor = connect_db()

        query = 'SELECT drink.drink_id, drink.image, drink.name, drink.price, stock.stock, drink.status FROM drink LEFT JOIN stock ON drink.drink_id = stock.drink_id;'
        cursor.execute(query)

        emp = get_emp_info(cursor)

    except mysql.connector.Error as err:
        printError(err)
    else:
        cnx.close()
    return render_template("emp_info.html", emp=emp)

#社員検索
@app.route('/emp_search', methods=['GET','POST'])
def emp_search():
    return render_template("emp_search.html")

#社員情報編集
@app.route('/emp_edit', methods=['GET','POST'])
def emp_edit():
    return render_template("emp_edit.html")

#社員情報編集結果
@app.route('/emp_edit_result', methods=['GET','POST'])
def emp_edit_result():
    return render_template("emp_edit_result.html")

#部署情報
@app.route('/de_info', methods=['GET','POST'])
def de_info():
    return render_template("de_info.html")

@app.route('/de_edit', methods=['GET','POST'])
def de_edit():
    return render_template("de_edit.html")

#部署情報編集結果
@app.route('/de_edit_result', methods=['GET','POST'])
def de_edit_result():
    return render_template("de_edit_result.html")