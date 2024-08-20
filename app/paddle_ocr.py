#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/10 10:50
# @function: the script is used to do something.
# @version : V1
import os
import cv2
import numpy
from paddlex import OCRPipeline
from paddlex import PaddleInferenceOption
from paddlex.pipelines.OCR.utils import draw_ocr_box_txt

# 实例化 PaddleInferenceOption 设置推理配置
kernel_option = PaddleInferenceOption()
kernel_option.set_device("gpu:0")

pipeline = OCRPipeline(
    'PP-OCRv4_server_det',
    'PP-OCRv4_server_rec',
    text_det_kernel_option=kernel_option,
    text_rec_kernel_option=kernel_option,
    output=None,
    device='gpu',
)


def dt_polys_analysis(dt_polys: numpy.ndarray):
    """
    dt_polys: numpy.ndarray
    """
    list = []
    for item in dt_polys.tolist():
        location = {
            "top": item[0][1],
            "left": item[0][0],
            "width": item[1][0] - item[0][0],
            "height": item[2][1] - item[1][1]
        }
        list.append(location)
    return list


def prob_map_analysis(prob_map: numpy.ndarray):
    """
    prob_map是一个二维矩阵,大小与输入图像大小相同
    每个像素点的值代表了该位置属于文本区域的概率。值越大,表示越可能是文本区域。
    prob_map与前面提到的dt_scores是相辅相成的。dt_scores给出了单个文本框的检测得分,而prob_map则描述了整个图像中文本区域的概率分布。
    prob_map: numpy.ndarray
    """
    arr = numpy.array(prob_map)
    print(arr.shape)
    for item in prob_map:
        print(item)
    return prob_map


def rec_text_analysis(rec_text: list):
    """
    rec_text: list
    """
    return rec_text


def dt_scores_analysis(dt_scores: list):
    """
    dt_scores: numpy.ndarray
    """
    return dt_scores


def original_image_analysis(original_image: numpy.ndarray):
    """
    original_image: numpy.ndarray
    """
    arr = numpy.array(original_image)
    print(f"original_image shape is:{arr.shape}")
    return original_image


def image_analysis(image: numpy.ndarray):
    """
    image: numpy.ndarray
    """
    arr = numpy.array(image)
    print(f"image shape is:{arr.shape}")
    return image


def predict(input_path, output_path=None):
    # # 将./data/input下的所有文件进行OCR识别
    result = pipeline.predict({"input_path": input_path})
    if output_path is not None:
        draw_img = draw_ocr_box_txt(result['original_image'], result['dt_polys'], result["rec_text"])
        cv2.imwrite(output_path, draw_img[:, :, ::-1])
    # 识别结果需要解析
    rec_text = rec_text_analysis(result['rec_text'])
    dt_polys = dt_polys_analysis(result['dt_polys'])
    dt_scores = dt_scores_analysis(result['dt_scores'])
    return [{'words': text, 'location': loc, 'score': score} for text, loc, score in zip(rec_text, dt_polys, dt_scores)]
