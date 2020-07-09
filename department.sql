/*最低限、以下のデータを管理します。

部署ID
部署名*/

CREATE TABLE department(
    department_id VARCHAR(255),
    department VARCHAR(255),
    department_register_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
    department_update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);