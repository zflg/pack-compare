#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/9 22:48
# @function: the script is used to do something.
# @version : V1
import requests
import json
import time
import numpy as np
import utils
import cv2
from setting import BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY
from paddlex.pipelines.OCR.utils import draw_ocr_box_txt


class BaiduClient:
    def __init__(self, app_id=BAIDU_APP_ID, api_key=BAIDU_API_KEY, secret_key=BAIDU_SECRET_KEY):
        self.access_token = None
        self.expires_in = None
        self.app_id = app_id
        self.api_key = api_key
        self.secret_key = secret_key

    def draw_ocr_box_txt(self, input_path, output_path, prediction):
        """
        Draw the OCR box on the image.

        @param input_path: the path of the image
        @param output_path: the path of the image with OCR box
        @param prediction: the prediction result of the OCR model
        """
        points = []
        words = []
        for item in prediction:
            words.append(item['words'])
            points.append(utils.location_to_point(item['location']))

        nd_points = np.array(points)
        image_blob = cv2.imread(input_path)

        draw_img = draw_ocr_box_txt(image_blob, nd_points, words)
        cv2.imwrite(output_path, draw_img[:, :, ::-1])

    def authenticate(self):
        """
        获取百度AI平台的token
        """
        if self.expires_in and self.expires_in > time.time():
            return
        url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = ""
        response = requests.request("POST", url, headers=headers, data=payload)
        body = json.loads(response.text)
        self.access_token = body['access_token']
        self.expires_in = time.time() + body['expires_in']

    def general_ocr(self,
                    base64_image,
                    probability='true',
                    detect_direction='true',
                    multidirectional_recognize='true'):
        """
        使用百度AI平台的标准OCR接口进行图片识别
        @param base64_image: 图片base64编码
        @param probability: 是否返回识别结果中每一行的置信度
        @param detect_direction: 是否检测图像朝向
        @param multidirectional_recognize: 是否开启多方向识别
        """
        if base64_image is None or len(base64_image) == 0:
            return
        self.authenticate()
        request_url = f'https://aip.baidubce.com/rest/2.0/ocr/v1/general?access_token={self.access_token}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        params = {
            'image': base64_image,
            'probability': probability,
            'detect_direction': detect_direction,
            'multidirectional_recognize': multidirectional_recognize
        }
        response = requests.post(request_url, data=params, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)['words_result']
        else:
            print(f"Failed to call Baidu general OCR API, status code: {response.status_code}")

    def accuracy_ocr(self,
                     base64_image,
                     probability='true',
                     detect_direction='true',
                     multidirectional_recognize='true'):
        """
        使用百度AI平台的高精度OCR接口进行图片识别
        @param base64_image: 图片base64编码
        @param probability: 是否返回识别结果中每一行的置信度
        @param detect_direction: 是否检测图像朝向
        @param multidirectional_recognize: 是否开启多方向识别
        """
        if base64_image is None or len(base64_image) == 0:
            return
        self.authenticate()
        request_url = f'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token={self.access_token}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        params = {
            'image': base64_image,
            'probability': probability,
            'detect_direction': detect_direction,
            'multidirectional_recognize': multidirectional_recognize
        }
        response = requests.post(request_url, data=params, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)['words_result']
        else:
            print(f"Failed to call Baidu accuracy OCR API, status code: {response.status_code}")
