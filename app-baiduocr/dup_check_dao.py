#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/9/25 17:25
# @function: the script is used to do something.
# @version : V1
import pymysql
import setting
import logging

connection = pymysql.connect(
    host=setting.MYSQL_HOST,
    user=setting.MYSQL_USER,
    password=setting.MYSQL_PASSWORD,
    db=setting.MYSQL_DATABASE,
    port=setting.MYSQL_PORT,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
logging.info("Database connected!")


class DupCheck:

    def __init__(self, id=None, ocrId=None, scLicense=None, sampleName=None, produceDate=None, bzLicense=None, createTime=None):
        self.id = id
        self.ocrId = ocrId
        self.scLicense = scLicense
        self.sampleName = sampleName
        self.produceDate = produceDate
        self.bzLicense = bzLicense
        self.createTime = createTime


class DupCheckOcr:

    def __init__(self, id=None, scLicense=None, sampleName=None, produceDate=None, bzLicense=None, screenshotUrl=None, screenshotOutputUrl=None, isDup=None,
                 createTime=None):
        self.id = id
        self.scLicense = scLicense
        self.sampleName = sampleName
        self.produceDate = produceDate
        self.bzLicense = bzLicense
        self.screenshotUrl = screenshotUrl
        self.screenshotOutputUrl = screenshotOutputUrl
        self.isDup = isDup
        self.createTime = createTime


def save_ocr(ocr: DupCheckOcr):
    """
    Save ocr to database.
    Args:
        ocr:

    Returns:
    """
    connection.ping(reconnect=True)
    sql = ("INSERT INTO `spl_dup_check_ocr` ("
           "`sc_license`,"
           "`sample_name`,"
           "`produce_date`,"
           "`bz_license`,"
           "`screenshot_url`,"
           "`screenshot_output_url`,"
           "`is_dup`,"
           "`create_time`)"
           " VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())")
    values = (
        ocr.scLicense,
        ocr.sampleName,
        ocr.produceDate,
        ocr.bzLicense,
        ocr.screenshotUrl,
        ocr.screenshotOutputUrl,
        1 if ocr.isDup else 0
    )
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    try:
        print(sql)
        cursor.execute(sql, values)
        # 找到最新插入的id
        ocr_id = connection.insert_id()
        ocr.id = ocr_id
        connection.commit()
        logging.info(f"OCR saved: {ocr}")
        return ocr
    except Exception as e:
        logging.exception(f"Save OCR failed: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()


def select_ocr_list(ocr: DupCheckOcr = None):
    """
    Select ocr list from database.
    Args:
        ocr

    Returns:
        Ocr list
    """
    sql = "SELECT * FROM `spl_dup_check_ocr` WHERE 1 = 1"
    if ocr is not None:
        if ocr.id is not None:
            sql += f" AND `id` = {ocr.id}"
        if ocr.scLicense is not None:
            sql += f" AND `sc_license` = '{ocr.scLicense}'"
        if ocr.sampleName is not None:
            sql += f" AND `sample_name` = '{ocr.sampleName}'"
        if ocr.produceDate is not None:
            sql += f" AND `produce_date` = '{ocr.produceDate}'"
        if ocr.bzLicense is not None:
            sql += f" AND `bz_license` = '{ocr.bzLicense}'"
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    cursor.execute(sql)
    ocr_list = cursor.fetchall()
    connection.commit()
    cursor.close()
    result = []
    if ocr_list is None:
        return result
    for ocr in ocr_list:
        result.append(DupCheckOcr(ocr['id'], ocr['sc_license'], ocr['sample_name'], ocr['produce_date'], ocr['bz_license'],
                                  ocr['screenshot_url'], ocr['screenshot_output_url'], ocr['is_dup'], ocr['create_time']))
    return result


def get_ocr_by_id(ocr_id: int):
    """
    Get ocr by id.
    Args:
        ocr_id

    Returns:
        ocr
    """
    sql = "SELECT * FROM `spl_dup_check_ocr` WHERE `id` = %s"
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    cursor.execute(sql, ocr_id)
    ocr = cursor.fetchone()
    connection.commit()
    cursor.close()
    if ocr is None:
        return None
    return DupCheckOcr(ocr['id'], ocr['sc_license'], ocr['sample_name'], ocr['produce_date'], ocr['bz_license'],
                       ocr['screenshot_url'], ocr['screenshot_output_url'], ocr['is_dup'], ocr['create_time'])


def select_dup_check_list(dupCheck: DupCheck = None):
    """
    Select dup check list from database.
    Args:
        dupCheck

    Returns:
        DupCheck list
    """
    sql = "SELECT * FROM `spl_dup_check` WHERE 1 = 1"
    if dupCheck is not None:
        if dupCheck.ocrId is not None:
            sql += f" AND `ocr_id` = '{dupCheck.ocrId}'"
        if dupCheck.scLicense is not None:
            sql += f" AND `sc_license` = '{dupCheck.scLicense}'"
        if dupCheck.sampleName is not None:
            sql += f" AND `sample_name` = '{dupCheck.sampleName}'"
        if dupCheck.produceDate is not None:
            sql += f" AND `produce_date` = '{dupCheck.produceDate}'"
        if dupCheck.bzLicense is not None:
            sql += f" AND `bz_license` = '{dupCheck.bzLicense}'"
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    print(sql)
    cursor.execute(sql)
    dup_check_list = cursor.fetchall()
    connection.commit()
    cursor.close()
    result = []
    if dup_check_list is None:
        return result
    for dup_check in dup_check_list:
        result.append(DupCheck(dup_check['id'], dup_check['ocr_id'], dup_check['sc_license'], dup_check['sample_name'], dup_check['produce_date'],
                               dup_check['bz_license'], dup_check['create_time']))
    return result


def save_dup_check(dupCheck: DupCheck):
    """
    Save dup check to database.
    Args:
        dupCheck:

    Returns:
    """
    connection.ping(reconnect=True)
    sql = ("INSERT INTO `spl_dup_check` ("
           "`ocr_id`,"
           "`sc_license`,"
           "`sample_name`,"
           "`produce_date`,"
           "`bz_license`,"
           "`create_time`)"
           " VALUES (%s, %s, %s, %s, %s, NOW())")
    values = (
        dupCheck.ocrId,
        dupCheck.scLicense,
        dupCheck.sampleName,
        dupCheck.produceDate,
        dupCheck.bzLicense
    )
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    try:
        cursor.execute(sql, values)
        # 找到最新插入的id
        id = connection.insert_id()
        dupCheck.id = id
        connection.commit()
        logging.info(f"Save dup check: {dupCheck}")
        return dupCheck
    except Exception as e:
        logging.exception(f"Save dup check failed: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
