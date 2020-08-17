import re

from flask import Flask, flash, request, redirect, render_template, url_for, session
import mysql.connector


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