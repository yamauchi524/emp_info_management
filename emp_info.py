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

#社員情報
@app.route('/emp_info', methods=['GET','POST'])
def emp_info():
    return render_template("emp_info.html")

#社員検索
@app.route('/emp_search', methods=['GET','POST'])
def emp_search():
    return render_template("emp_search.html")

#社員情報編集
@app.route('/emp_edit', methods=['GET','POST'])
def emp_edit():
    return render_template("emp_edit.html")

#部署情報
@app.route('/de_info', methods=['GET','POST'])
def de_info():
    return render_template("de_info.html")

@app.route('/de_edit', methods=['GET','POST'])
def de_edit():
    return render_template("de_edit.html")