/*[証明写真テーブル]
最低限、以下のデータを管理します。

写真ID
画像データ

画像データのファイル形式については、JPEG形式およびPNG形式のみとします。*/

CREATE TABLE image(
    image_id VARCHAR(255),
    image VARCHAR(255),
    image_register_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
    image_update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY(image_id)
);

insert into image(image_id, image) value('7we4CMGj', './static/man04.png');
insert into image(image_id, image) value('woccb8Vn', './static/woman01.png');