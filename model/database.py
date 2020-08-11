import datetime

import mysql.connector
from mysql.connector import errorcode
from model.const import DB

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

#社員情報の取得
def get_emp_info(cursor):
    emp = []
    for (emp_id, name, age, gender, image, postal_code, pref, address, department, join_date, leave_date) in cursor:
        data = {"emp_id":emp_id, "name":name, "age":age, "gender":gender, "image":image, "postal_code":postal_code, "pref":pref, "address":address, "department":department, "join_date":join_date, "leave_date":leave_date}
        emp.append(data)
    return emp
