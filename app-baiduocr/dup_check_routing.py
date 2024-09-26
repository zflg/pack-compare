#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/9/25 12:53
# @function: the script is used to do something.
# @version : V1
from flask import Blueprint, request, jsonify
from client import baiduClient
from setting import NGINX_ROOT
from kie import ScreenShotKie
from utils import similarity_threshold_check

import os
import time
import base64
import dup_check_dao as dao

dup_check_bp = Blueprint('dup_check_bp', __name__)

THRESHOLD = {
    "scLicense": 0.9,
    "sampleName": 0.6,
    "produceDate": 1,
    "bzLicense": 0.9
}

result = {
    "content": {
        "scLicense": "SC111111111111",
        "sampleName": "台湾无骨鸡爪",
        "produceDate": "2024-09-25",
        "bzLicense": "BZ111111111111"
    },
    "isDup": False,
    "dupInfo": {
        "id": 1,
        "createTime": "2024-09-25 12:00:00",
        "scLicense": "SC111111111111",
        "sampleName": "台湾无骨鸡爪",
        "produceDate": "2024-09-25",
        "bzLicense": "BZ111111111111",
        "ocrId": 10,
        "screenshotUrl": "dupCheck/input/20240925-120000.jpg",
        "screenshotOutputUrl": "dupCheck/output/20240925-120000.jpg",

    },
    "refInfo": {
        "scLicense": {
            # 相似度阈值
            "threshold": 0.9,
            # hasRef为True表示有参考值，False表示没有参考值(有没有找到历史数据，超过相似度阈值则认为找到了历史参照)
            "hasRef": True,
            # 找到历史数据之后的纠错结果,这是一个列表
            "refs": [
                {
                    "id": 1,
                    "content": "SC111111111112",
                    "similarity": 0.92
                },
                {
                    "id": 2,
                    "content": "SC111111111113",
                    "similarity": 0.92
                }
            ]
        },
        "sampleName": {
            # 相似度阈值更低
            "threshold": 0.6,
            "hasRef": True,
            "refs": [
                {
                    "id": 1,
                    "content": "台湾无骨鸭爪",
                    "similarity": 0.86
                },
            ]
        },
        "produceDate": {
            # 不做参考所以相似度阈值为1
            "threshold": 1,
            "hasRef": False,
            "refs": None
        },
        "bzLicense": {
            "threshold": 0.9,
            "hasRef": False,
            "refs": []
        },
    }
}

# 如果根目录不存在，则创建目录
if os.path.exists(f'{NGINX_ROOT}/dupCheck/input') is False:
    os.makedirs(f'{NGINX_ROOT}/dupCheck/input')
# 如果根目录不存在，则创建目录
if os.path.exists(f'{NGINX_ROOT}/dupCheck/output') is False:
    os.makedirs(f'{NGINX_ROOT}/dupCheck/output')


def save_image(base64_image):
    # 保存文件
    file_name = time.strftime('%Y%m%d-%H%M%S') + '.jpg'
    file_url = f'dupCheck/input/{file_name}'
    # 将base64编码的图片数据写入文件，文件名为当前时间戳
    if base64_image.startswith('data:image/jpeg;base64,'):
        base64_image = base64_image.replace('data:image/jpeg;base64,', '')
    imgdata = base64.b64decode(base64_image)
    with open(f"{NGINX_ROOT}/{file_url}", "wb") as f:
        f.write(imgdata)
    return file_url


def get_output_url(input_url):
    output_url = input_url.replace('input', 'output')
    output_dir = '/'.join(output_url.split('/')[:-1])
    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)
    return output_url


def check(ocr: dao.DupCheckOcr):
    """
    检查OCR结果
    Args:
        ocr:

    Returns:
        result
    """
    all = dao.select_dup_check_list()
    result = {}
    # 检查是否有重复
    for item in all:
        if item.scLicense == ocr.scLicense and item.sampleName == ocr.sampleName and item.produceDate == ocr.produceDate and item.bzLicense == ocr.bzLicense:
            dup = item
            ocr = dao.get_ocr_by_id(item.ocrId)
            dupInfo = {
                "id": dup.id,
                "createTime": dup.createTime,
                "scLicense": dup.scLicense,
                "sampleName": dup.sampleName,
                "produceDate": dup.produceDate,
                "bzLicense": dup.bzLicense,
                "ocrId": ocr.id,
                "screenshotUrl": ocr.screenshotUrl,
                "screenshotOutputUrl": ocr.screenshotOutputUrl,
            }
            result['isDup'] = True
            result['dupInfo'] = dupInfo
    if 'isDup' not in result:
        result['isDup'] = False
    # 检查相似度
    refInfo = {
        "scLicense": {
            # 相似度阈值
            "threshold": THRESHOLD['scLicense'],
            # hasRef为True表示有参考值，False表示没有参考值(有没有找到历史数据，超过相似度阈值则认为找到了历史参照)
            "hasRef": False,
            # 找到历史数据之后的纠错结果,这是一个列表
            "refs": []
        },
        "sampleName": {
            # 相似度阈值更低
            "threshold": THRESHOLD['sampleName'],
            "hasRef": False,
            "refs": []
        },
        "produceDate": {
            "threshold": THRESHOLD['produceDate'],
            "hasRef": False,
            "refs": None
        },
        "bzLicense": {
            "threshold": THRESHOLD['bzLicense'],
            "hasRef": False,
            "refs": []
        },
    }
    for item in all:
        hasRef, ratios = similarity_threshold_check(item.scLicense, ocr.scLicense, THRESHOLD['scLicense'])
        if hasRef:
            refInfo['scLicense']['hasRef'] = True
            refInfo['scLicense']['refs'].append({
                "id": item.id,
                "content": item.scLicense,
                "similarity": ratios
            })
        hasRef, ratios = similarity_threshold_check(item.sampleName, ocr.sampleName, THRESHOLD['sampleName'])
        if hasRef:
            refInfo['sampleName']['hasRef'] = True
            refInfo['sampleName']['refs'].append({
                "id": item.id,
                "content": item.sampleName,
                "similarity": ratios
            })
        hasRef, ratios = similarity_threshold_check(item.bzLicense, ocr.bzLicense, THRESHOLD['bzLicense'])
        if hasRef:
            refInfo['bzLicense']['hasRef'] = True
            refInfo['bzLicense']['refs'].append({
                "id": item.id,
                "content": item.bzLicense,
                "similarity": ratios
            })

    return result


@dup_check_bp.route('/dup_check', methods=['POST'])
def dup_check():
    # 从请求中获取JSON数据
    data = request.get_json()
    base64_screenshot = data['screenshot']
    # 保存图片
    input_url = save_image(base64_screenshot)
    output_url = get_output_url(input_url)
    # 百度ocr预测
    prediction = baiduClient.accuracy_ocr(base64_screenshot)
    baiduClient.draw_ocr_box_txt(f'{NGINX_ROOT}/{input_url}', f'{NGINX_ROOT}/{output_url}', prediction)
    extract_info = ScreenShotKie(prediction).run()
    # 保存结果
    ocr = dao.save_ocr(extract_info)
    if ocr is None:
        return jsonify({"error": "OCR save failed"})
    # check然后返回check结果
    return jsonify(check(ocr))
