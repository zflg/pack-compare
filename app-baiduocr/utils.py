#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/11 17:09
# @function: the script is used to do something.
# @version : V1
import difflib


def location_to_point(location):
    """
    将baiduOCR返回的位置数据转化为坐标数据
    Args:
        location: {"top": 337,"left": 385,"width": 244,"height": 61}
    Returns:
        list: [[385, 337], [385 + 244, 337], [385 + 244, 337 + 61], [385, 337 + 61]]
    """
    return [[location['left'], location['top']],
            [location['left'] + location['width'], location['top']],
            [location['left'] + location['width'], location['top'] + location['height']],
            [location['left'], location['top'] + location['height']]]


def point_to_location(point):
    """
    将坐标数据转化为baiduOCR返回的位置数据
    Args:
        point: [[385, 337], [629, 337], [629, 398], [385, 398]]
    Returns:
        {"top": 337,"left": 385,"width": 244,"height": 61}
    """
    location = {
        "top": point[0][1],
        "left": point[0][0],
        "width": point[1][0] - point[0][0],
        "height": point[2][1] - point[1][1]
    }
    return location


def similarity_threshold_check(content: str, ref_content: str, threshold: float = 0.9):
    """
    检查两个文本的相似度是否超过阈值
    Args:
        content: 文本1
        ref_content: 文本2
        threshold: 阈值，范围[0, 1]，默认0.9
    Returns:
        bool: True表示相似度超过阈值，False表示相似度没有超过阈值
    """
    if not content or not ref_content:
        return False, None
    if threshold >= 1:
        return False, None
    similarity = difflib.SequenceMatcher(None, content, ref_content).ratio()
    return similarity >= threshold, similarity


if __name__ == '__main__':
    print(similarity_threshold_check("SC1234567890123", "SC12345678901234", 0.9))
