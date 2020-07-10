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
    id INT AUTO_INCREMENT,
    emp_id VARCHAR(255),
    name VARCHAR(255),
    age INT UNSIGNED,
    gender VARCHAR(255),
    image_id VARCHAR(255), 
    postal_code INT(7) UNSIGNED,
    pref VARCHAR(100),
    address VARCHAR(255),
    department_id VARCHAR(255),
    join_date DATE,
    leave_date DATE,
    register_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
    update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
);
