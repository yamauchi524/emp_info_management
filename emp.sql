/*[社員情報テーブル]
最低限、以下のデータを管理します。

社員ID
名前
年齢
性別
写真ID
住所
部署ID
入社日
退社日*/

CREATE TABLE emp(
    emp_id VARCHAR(255),
    name VARCHAR(255),
    age INT UNSIGNED,
    gender VARCHAR(255),
    image_id VARCHAR(255), 
    postal_code VARCHAR(8),
    pref VARCHAR(100),
    address VARCHAR(255),
    department_id INT,
    join_date DATE,
    leave_date DATE,
    register_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
    update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY(emp_id)
);

insert into emp(emp_id,name,age,gender,image_id,postal_code,pref,address,department_id,join_date,leave_date) values('emp0001','田中太郎', 24, '男', '7we4CMGj','100-1000','東京都','千代田区', 1, '2020-04-01','9999-03-31');
insert into emp(emp_id,name,age,gender,image_id,postal_code,pref,address,department_id,join_date,leave_date) values('emp0002','日本花子', 27, '女', 'woccb8Vn','200-2000','埼玉県','さいたま市', 2, '2017-04-01','9999-03-31');
insert into emp(emp_id,name,age,gender,image_id,postal_code,pref,address,department_id,join_date,leave_date) values('emp0003','東京次郎', 32, '男', 'QvNBr6Xb', '300-3000','神奈川県','川崎市', 3, '2020-04-01','9999-03-31');