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


class Sample:

    def __init__(self, sample_no, metadata, ocr_checked):
        self.cursor = connection.cursor()
        self.sample_no = sample_no
        self.metadata = json.loads(metadata)
        self.ocr_checked = ocr_checked

    def get_producer(self):
        """
        Get producer from metadata.
        Returns:
        """
        return self.metadata['producer'] if 'producer' in self.metadata else None

    def get_sc_license(self):
        """
        Get sc_license from metadata.
        Returns:
        """
        return self.metadata['sc_license'] if 'sc_license' in self.metadata else None

    def get_expiration_time(self):
        """
        Get expiration_time from metadata.
        Returns:
        """
        return self.metadata['expiration_time'] if 'expiration_time' in self.metadata else None


def get_ocr(sample_no):
    """
    Get OCR result from database.
    Args:
        sample_no:

    Returns:
        Ocr
    """
    sql = "SELECT * FROM `spl_pack_compare_ocr` WHERE `sample_no` = %s"
    cursor = connection.cursor()
    cursor.execute(sql, sample_no)
    ocr = cursor.fetchone()
    cursor.close()
    if ocr is None:
        return None
    return Ocr(ocr['sample_no'], ocr['image_path'], ocr['ocr_type'], ocr['ocr_result'], ocr['extract_info'])


def save_ocr(ocr):
    """
    Save OCR result to database.
    Args:
        ocr
    """
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
        print(f"OCR {ocr.sample_no} saved to database")
    except Exception as e:
        print(f"Failed to save OCR result of sample {ocr.sample_no} to database: {e}")
        connection.rollback()
    cursor.close()


def get_sample(sample_no):
    """
    Get sample metadata from database
    Args:
        sample_no

    Returns:
        Sample
    """
    sql = "SELECT * FROM `spl_sample` WHERE `sample_no` = %s"
    cursor = connection.cursor()
    cursor.execute(sql, sample_no)
    sample = cursor.fetchone()
    cursor.close()
    if sample is None:
        return None
    return Sample(sample['sample_no'], sample['metadata'], sample['ocr_checked'])


def save_sample_ocr_checked(sample_no):
    """
    Save sample OCR result to database.
    Args:
        sample_no
    """
    sql = ("UPDATE `spl_sample` SET `ocr_checked` = 1, `ocr_checked_time` = NOW() WHERE `sample_no` = %s")
    cursor = connection.cursor()
    try:
        cursor.execute(sql, sample_no)
        connection.commit()
        print(f"Sample {sample_no} orc checked")
    except Exception as e:
        print(f"Failed to save Sample {sample_no} orc checked: {e}")
        connection.rollback()
    cursor.close()
