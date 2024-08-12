#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/9 22:42
# @function: the script is used to do something.
# @version : V1
from flask import Flask, request, jsonify
from client import BaiduClient
from pack_compare_dao import Ocr, OcrType, save_ocr
from kie import FoodPackKIE

import os
import time
import base64
import paddle_ocr

app = Flask(__name__)
baiduClient = BaiduClient()
IMAGE_ROOT = 'E:/data/ocr_images/'


def predict_with_ai_model(data):
    res = baiduClient.accuracy_ocr(data['image'])
    for item in res['words_result']:
        print(item['words'])
    return res


def save_image(base64_image):
    # 如果根目录不存在，则创建目录
    if os.path.exists(IMAGE_ROOT) is False:
        os.makedirs(IMAGE_ROOT)
    # 打开文件目录，文件目录是/项目根目录/ocr_images/年-月-日
    dir_path = f"{IMAGE_ROOT}/{time.strftime('%Y-%m-%d')}"
    if os.path.exists(dir_path) is False:
        os.makedirs(dir_path)
    # 保存文件
    file_path = f"{dir_path}/{int(time.time())}.jpg"
    # 将base64编码的图片数据写入文件，文件名为当前时间戳
    head, context = base64_image.split(",")
    imgdata = base64.b64decode(context)
    with open(file_path, "wb") as f:
        f.write(imgdata)
    return file_path


def get_output_file_path(input_file_path):
    output_file_path = input_file_path.replace('ocr_images', 'ocr_images_output')
    output_dir = '/'.join(output_file_path.split('/')[:-1])
    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)
    return output_file_path


@app.route('/ocr/predict', methods=['POST'])
def predict():
    # 从请求中获取JSON数据
    data = request.get_json()
    base64_image = data['image']
    # 保存图片
    image_path = save_image(base64_image)
    # BAIDU OCR预测
    # prediction = baiduClient.accuracy_ocr(base64_image)
    # extract_info = FoodPackKIE(prediction).run()
    # save_ocr(Ocr(None, image_path, OcrType.BAIDU_OCR,prediction, extract_info))
    # PADDLE OCR预测，可画出识别框
    output_path = get_output_file_path(image_path)
    prediction = paddle_ocr.predict(image_path, output_path)
    extract_info = FoodPackKIE(prediction).run()
    print(extract_info)
    save_ocr(Ocr(None, image_path, OcrType.PADDLE_OCR, prediction, extract_info))
    # 将预测结果作为响应返回
    return jsonify(prediction)


if __name__ == '__main__':
    # 运行Flask应用，监听8000端口
    app.run(port=8000, debug=True)
