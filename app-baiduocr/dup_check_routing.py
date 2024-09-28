#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/9/25 12:53
# @function: the script is used to do something.
# @version : V1
import datetime

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
    "scLicense": 1,
    "sampleName": 0.8,
    "produceDate": 1,
    "bzLicense": 1
}

# result = {
#     "content": {
#         "scLicense": "SC111111111111",
#         "sampleName": "台湾无骨鸡爪",
#         "produceDate": "2024-09-25",
#         "bzLicense": "BZ111111111111"
#     },
#     "isDup": False,
#     "dupInfo": {
#         "id": 1,
#         "createTime": "2024-09-25 12:00:00",
#         "scLicense": "SC111111111111",
#         "sampleName": "台湾无骨鸡爪",
#         "produceDate": "2024-09-25",
#         "bzLicense": "BZ111111111111",
#         "ocrId": 10,
#         "screenshotUrl": "dupCheckFiles/input/20240925-120000.jpg",
#         "screenshotOutputUrl": "dupCheckFiles/output/20240925-120000.jpg",
#
#     },
#     "refInfo": {
#         "scLicense": {
#             # 相似度阈值
#             "threshold": 0.9,
#             # hasRef为True表示有参考值，False表示没有参考值(有没有找到历史数据，超过相似度阈值则认为找到了历史参照)
#             "hasRef": True,
#             # 找到历史数据之后的纠错结果,这是一个列表
#             "refs": [
#                 {
#                     "id": 1,
#                     "content": "SC111111111112",
#                     "similarity": 0.92
#                 },
#                 {
#                     "id": 2,
#                     "content": "SC111111111113",
#                     "similarity": 0.92
#                 }
#             ]
#         },
#         "sampleName": {
#             # 相似度阈值更低
#             "threshold": 0.6,
#             "hasRef": True,
#             "refs": [
#                 {
#                     "id": 1,
#                     "content": "台湾无骨鸭爪",
#                     "similarity": 0.86
#                 },
#             ]
#         },
#         "produceDate": {
#             # 不做参考所以相似度阈值为1
#             "threshold": 1,
#             "hasRef": False,
#             "refs": None
#         },
#         "bzLicense": {
#             "threshold": 0.9,
#             "hasRef": False,
#             "refs": []
#         },
#     }
# }

# prediction = [{'probability': {'average': 0.9992135763, 'min': 0.9927974343, 'variance': 4.576815172e-06}, 'words': '10:239月26日',
#                'location': {'top': 11, 'left': 47, 'width': 193, 'height': 32}},
#               {'probability': {'average': 0.9999781847, 'min': 0.9999598265, 'variance': 3.370246304e-10}, 'words': '周四',
#                'location': {'top': 12, 'left': 251, 'width': 59, 'height': 31}},
#               {'probability': {'average': 0.9999492764, 'min': 0.9999064207, 'variance': 1.836614416e-09}, 'words': '45',
#                'location': {'top': 20, 'left': 1481, 'width': 25, 'height': 16}},
#               {'probability': {'average': 0.9994804263, 'min': 0.9994804263, 'variance': 0}, 'words': '<',
#                'location': {'top': 86, 'left': 33, 'width': 28, 'height': 43}},
#               {'probability': {'average': 0.9994714856, 'min': 0.9991490841, 'variance': 7.827444648e-08}, 'words': '样品填报',
#                'location': {'top': 87, 'left': 722, 'width': 152, 'height': 41}},
#               {'probability': {'average': 0.9997881055, 'min': 0.99935776, 'variance': 6.241887718e-08}, 'words': 'SC号：',
#                'location': {'top': 306, 'left': 71, 'width': 94, 'height': 36}},
#               {'probability': {'average': 0.9999607801, 'min': 0.9998807907, 'variance': 1.078768186e-09}, 'words': 'SC10634122207025',
#                'location': {'top': 309, 'left': 411, 'width': 324, 'height': 32}},
#               {'probability': {'average': 0.9996398091, 'min': 0.9983696342, 'variance': 4.064296775e-07}, 'words': '样本名称：',
#                'location': {'top': 488, 'left': 70, 'width': 159, 'height': 38}},
#               {'probability': {'average': 0.9999471307, 'min': 0.9998549223, 'variance': 3.236055202e-09}, 'words': '云南黑咖啡固体饮料',
#                'location': {'top': 491, 'left': 410, 'width': 325, 'height': 38}},
#               {'probability': {'average': 0.999538064, 'min': 0.9977224469, 'variance': 8.240952525e-07}, 'words': '生产日期：',
#                'location': {'top': 673, 'left': 71, 'width': 157, 'height': 38}},
#               {'probability': {'average': 0.9999939203, 'min': 0.9999756813, 'variance': 6.591136664e-11}, 'words': '2024-06-02',
#                'location': {'top': 678, 'left': 409, 'width': 186, 'height': 33}},
#               {'probability': {'average': 0.9994578362, 'min': 0.9970893264, 'variance': 1.131303293e-06}, 'words': '营业执照号：',
#                'location': {'top': 857, 'left': 72, 'width': 193, 'height': 39}},
#               {'probability': {'average': 0.9661802053, 'min': 0.6637955308, 'variance': 0.01015981846}, 'words': 'GB/T 29602',
#                'location': {'top': 861, 'left': 410, 'width': 200, 'height': 38}},
#               {'probability': {'average': 0.9982610941, 'min': 0.9966891408, 'variance': 2.471130756e-06}, 'words': '清除',
#                'location': {'top': 1037, 'left': 800, 'width': 69, 'height': 33}}]

# 如果根目录不存在，则创建目录
if os.path.exists(f'{NGINX_ROOT}/dupCheckFiles/input') is False:
    os.makedirs(f'{NGINX_ROOT}/dupCheckFiles/input')
# 如果根目录不存在，则创建目录
if os.path.exists(f'{NGINX_ROOT}/dupCheckFiles/output') is False:
    os.makedirs(f'{NGINX_ROOT}/dupCheckFiles/output')


def save_image(base64_image):
    # 保存文件
    file_name = time.strftime('%Y%m%d-%H%M%S') + '.jpg'
    file_url = f'dupCheckFiles/input/{file_name}'
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


def check(extract_info: dict):
    """
    检查OCR结果
    Args:
        ocr:

    Returns:
        result
    """
    check_list = dao.select_dup_check_list()
    result = {
        "content": {
            "scLicense": extract_info['sc_license'],
            "sampleName": extract_info['sample_name'],
            "produceDate": extract_info['produce_date'],
            "bzLicense": extract_info['bz_license']
        }
    }
    # check_list按照时间倒叙
    check_list.sort(key=lambda x: x.createTime, reverse=True)
    # 检查是否有重复，只检查三个月内的数据
    check_time = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
    for item in check_list:
        if item.createTime < check_time:
            break
        if item.sampleName == extract_info['sample_name'] and item.bzLicense == extract_info['bz_license']:
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
            break
    if 'isDup' not in result:
        result['isDup'] = False
    # 检查相似度
    refInfo = {
        "scLicense": {
            # 相似度阈值
            "threshold": THRESHOLD['scLicense'],
            # hasRef为True表示有参考值，False表示没有参考值(有没有找到历史数据，超过相似度阈值则认为找到了历史参照)
            "hasRef": False,
            "hasSame": False,
            # 找到历史数据之后的纠错结果,这是一个列表
            "refs": None
        },
        "sampleName": {
            # 相似度阈值更低
            "threshold": THRESHOLD['sampleName'],
            "hasRef": False,
            "hasSame": False,
            "refs": []
        },
        "produceDate": {
            "threshold": THRESHOLD['produceDate'],
            "hasRef": False,
            "hasSame": False,
            "refs": None
        },
        "bzLicense": {
            "threshold": THRESHOLD['bzLicense'],
            "hasRef": False,
            "hasSame": False,
            "refs": None
        },
    }
    # 如果没有提取到sample_name则直接返回
    if extract_info["sample_name"] is None:
        result['refInfo'] = refInfo
        return result
    # 将check_list里面的sample_name做distinct处理
    for item in check_list:
        if item.sampleName == extract_info["sample_name"]:
            refInfo['sampleName']['hasSame'] = True
            break
    if refInfo['sampleName']['hasSame'] is False:
        sample_names = set()
        for item in check_list:
            if item.sampleName is None:
                continue
            if sample_names.__contains__(item.sampleName):
                continue
            sample_names.add(item.sampleName)
            hasRef, similarity = similarity_threshold_check(item.sampleName, extract_info["sample_name"], THRESHOLD['sampleName'])
            if hasRef:
                refInfo['sampleName']['hasRef'] = True
                refInfo['sampleName']['refs'].append({
                    "id": item.id,
                    "content": item.sampleName,
                    "similarity": similarity
                })
    result['refInfo'] = refInfo
    return result


def result_correct(result: dict):
    return (result["isDup"] is False
            and (result["refInfo"]["sampleName"]["hasSame"] is True
                 or result["refInfo"]["sampleName"]["hasRef"] is False)
            and (result["content"]["scLicense"] is not None
                 and result["content"]["sampleName"] is not None
                 and result["content"]["produceDate"] is not None
                 and result["content"]["bzLicense"] is not None))


@dup_check_bp.route('/ocr/dup-check', methods=['POST'])
def dup_check():
    # 从请求中获取JSON数据
    data = request.get_json()
    base64_screenshot = data['screenshot']
    # 保存图片
    input_url = save_image(base64_screenshot)
    output_url = get_output_url(input_url)
    # 百度ocr预测
    prediction = baiduClient.accuracy_ocr(base64_screenshot, detect_direction='false', multidirectional_recognize='false')
    print(f"prediction: {prediction}")
    baiduClient.draw_ocr_box_txt(f'{NGINX_ROOT}/{input_url}', f'{NGINX_ROOT}/{output_url}', prediction)
    extract_info = ScreenShotKie(prediction).run()
    print(f"extract_info: {extract_info}")
    if extract_info is None:
        return jsonify({"error": "OCR failed"})
    result = check(extract_info)
    # 保存结果
    isDup = result['isDup']
    ocr = dao.DupCheckOcr(None, extract_info['sc_license'], extract_info['sample_name'], extract_info['produce_date'],
                          extract_info['bz_license'], input_url, output_url, isDup, None)
    dao.save_ocr(ocr)
    if ocr is None:
        return jsonify({"error": "OCR save failed"})
    # 如果没有重复则保存
    if result_correct(result):
        dupCheck = dao.DupCheck(None, ocr.id, extract_info['sc_license'], extract_info['sample_name'], extract_info['produce_date'],
                                extract_info['bz_license'], None)
        dao.save_dup_check(dupCheck)
    # 返回结果
    return jsonify(result)


if __name__ == '__main__':
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
