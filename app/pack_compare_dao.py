#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/10 9:50
# @function: the script is used to do something.
# @version : V1

import pymysql
import setting
import json
from enum import Enum

connection = pymysql.connect(
    host=setting.MYSQL_HOST,
    user=setting.MYSQL_USER,
    password=setting.MYSQL_PASSWORD,
    db=setting.MYSQL_DATABASE,
    port=setting.MYSQL_PORT,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
print("Database connected!")


class OcrType(Enum):
    BAIDU_OCR = 'baidu_ocr'
    PADDLE_OCR = 'paddle_ocr'


class Ocr:

    def __init__(self, sample_no, image_path, ocr_type: OcrType, ocr_result, extract_info):
        self.cursor = connection.cursor()
        self.sample_no = sample_no
        self.ocr_type = ocr_type
        self.image_path = image_path
        self.ocr_result = ocr_result
        self.extract_info = extract_info


def get_ocr(sample_no):
    sql = "SELECT * FROM `ocr` WHERE `sample_no` = %s"
    cursor = connection.cursor()
    cursor.execute(sql, sample_no)
    ocr = cursor.fetchone()
    cursor.close()
    return Ocr(ocr['sample_no'], ocr['image_path'], ocr['ocr_type'], ocr['ocr_result'])


def save_ocr(ocr):
    sql = ("INSERT INTO `spl_pack_compare_ocr` (`sample_no`,"
           "`image_path`,"
           "`ocr_type`,"
           "`ocr_result`,"
           "`extract_info`,"
           "`create_time`,"
           "`update_time`) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())")
    values = (
        ocr.sample_no,
        ocr.image_path,
        ocr.ocr_type.value,
        json.dumps(ocr.ocr_result, ensure_ascii=False),
        json.dumps(ocr.extract_info, ensure_ascii=False)
    )
    cursor = connection.cursor()
    try:
        cursor.execute(sql, values)
        connection.commit()
        print(f"OCR result of sample {ocr.sample_no} saved to database")
    except Exception as e:
        print(f"Failed to save OCR result of sample {ocr.sample_no} to database: {e}")
        connection.rollback()
    cursor.close()
