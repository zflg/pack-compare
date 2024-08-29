#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/9 22:42
# @function: the script is used to do something.
# @version : V1
from flask import Flask, request, jsonify
from client import BaiduClient
from pack_compare_dao import Ocr, OcrType, save_ocr, get_ocr, get_sample, save_sample_ocr_checked
from kie import FoodPackKIE
from flask_cors import CORS

import os
import time
import base64
import paddle_ocr

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有源的跨域请求
baiduClient = BaiduClient()
NGINX_ROOT = 'E:/data/ocr_images'


# NGINX_ROOT = '/usr/local/webserver/nginx/html/aglimsFiles'


def predict_with_ai_model(data):
    res = baiduClient.accuracy_ocr(data['image'])
    for item in res['words_result']:
        print(item['words'])
    return res


def save_image(base64_image):
    # 保存文件
    file_name = time.strftime('%Y%m%d-%H%M%S') + '.jpg'
    file_url = f'ocrFiles/input/{file_name}'
    # 将base64编码的图片数据写入文件，文件名为当前时间戳
    head, context = base64_image.split(",")
    imgdata = base64.b64decode(context)
    with open(f"{NGINX_ROOT}/{file_url}", "wb") as f:
        f.write(imgdata)
    return file_url


def get_output_url(input_url):
    output_url = input_url.replace('input', 'output')
    output_dir = '/'.join(output_url.split('/')[:-1])
    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)
    return output_url


def orc_check(sample_no, extract_info):
    """
    Compare the OCR result with the database sample metadata.
    Args:
        sample_no:
        extract_info:

    Returns:
        orc_checked
    """
    # 获取样本信息
    sample = get_sample(sample_no)
    # 如果样本不存在，则返回False
    if sample is None:
        return False
    # 如果已经checked，则返回True
    if sample.ocr_checked == 1:
        return True
    # 对比生产商
    producer = sample.get_producer()
    if producer is not None and producer.strip() not in extract_info['producer']:
        return False
    # 对比SC许可证
    sc_license = sample.get_sc_license()
    if sc_license is not None and sc_license.strip() not in extract_info['sc_license']:
        return False
    # 对比过期时间
    expiration_time = sample.get_expiration_time()
    if expiration_time is not None and expiration_time.strip() not in extract_info['expiration_time']:
        return False
    # 保存OCR已经识别成功的结果
    save_sample_ocr_checked(sample_no)

    return True


def is_ocr_checked(sample_no):
    """
    Check if the OCR result has been checked.
    Args:
        sample_no:

    Returns:
        ocr_checked
    """
    sample = get_sample(sample_no)
    if sample is None:
        return False
    return sample.ocr_checked == 1


@app.route('/ocr/predict', methods=['POST'])
def predict():
    # 从请求中获取JSON数据
    data = request.get_json()
    base64_image = data['image']
    sample_no = data['sampleNo']
    # 检查是否已经checked
    # if is_ocr_checked(sample_no):
    #     ocr = get_ocr(sample_no)
    #     return jsonify({"ocr_checked": True, "extract_info": ocr.extract_info})
    # 保存图片
    image_url = save_image(base64_image)
    output_url = get_output_url(image_url)
    # BAIDU OCR预测
    prediction = baiduClient.accuracy_ocr(base64_image)
    baiduClient.draw_ocr_box_txt(f'{NGINX_ROOT}/{image_url}', f'{NGINX_ROOT}/{output_url}', prediction)
    extract_info = FoodPackKIE(prediction).run()
    save_ocr(Ocr(sample_no, image_url, output_url, OcrType.BAIDU_OCR, prediction, extract_info))
    # PADDLE OCR预测，可画出识别框
    # prediction = paddle_ocr.predict(f'{NGINX_ROOT}/{image_url}')
    # baiduClient.draw_ocr_box_txt(f'{NGINX_ROOT}/{image_url}', f'{NGINX_ROOT}/{output_url}', prediction)
    # extract_info = FoodPackKIE(prediction).run()
    # save_ocr(Ocr(sample_no, image_url, output_url, OcrType.PADDLE_OCR, prediction, extract_info))
    # 将OCR的结果和数据库比较
    # ocr_checked = orc_check(sample_no, extract_info)
    # 将预测结果作为响应返回
    return jsonify({"ocr_checked": True, "output_url": output_url, "extract_info": extract_info})


@app.route('/ocr/check-info', methods=['POST'])
def sample_info():
    # 从请求中获取JSON数据
    data = request.get_json()
    sample_no = data['sampleNo']
    # 获取样本信息
    sample = get_sample(sample_no)
    if sample is None:
        raise Exception(f"Sample {sample_no} not found.")
    # 对比生产商
    return jsonify({
        "producer": sample.get_producer(),
        "sc_license": sample.get_sc_license(),
        "expiration_time": sample.get_expiration_time()
    })


if __name__ == '__main__':
    # 如果根目录不存在，则创建目录
    if os.path.exists(f'{NGINX_ROOT}/ocrFiles/input') is False:
        os.makedirs(f'{NGINX_ROOT}/ocrFiles/input')
    # 如果根目录不存在，则创建目录
    if os.path.exists(f'{NGINX_ROOT}/ocrFiles/output') is False:
        os.makedirs(f'{NGINX_ROOT}/ocrFiles/output')
    # 运行Flask应用，监听8000端口
    app.run(port=8000, debug=True)
