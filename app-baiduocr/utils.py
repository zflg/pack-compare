#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/11 17:09
# @function: the script is used to do something.
# @version : V1
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


def extract_sc_license(boarding_boxes: list):
    """
    从boarding_boxes中提取SC证书号，可能提取多个，主要处理换行的情况
    Args:
        boarding_boxes: list
    Returns:
        sc license list
    """
    if (not boarding_boxes
            or not isinstance(boarding_boxes, list)
            or len(boarding_boxes) == 0
            or not boarding_boxes[0].get('words')):
        return []
    # 提取所有SC紧跟的数字
    sc_numbers = []
    # 提取所有纯数字
    pure_numbers = []
    # 遍历每个box
    for box in boarding_boxes:
        word = box['words']

        # 提取SC紧跟的数字
        import re
        sc_matches = re.findall(r'SC(\d{1,12})', word)
        for match in sc_matches:
            sc_numbers.append('SC' + match)

        # 提取纯数字
        number_matches = re.findall(r'\b\d+\b', word)  # 使用\b确保匹配的是完整的单词（即数字）
        for match in number_matches:
            pure_numbers.append(match)

    # 尝试拼接SC数字和纯数字以形成长度为14的字符串
    valid_pairs = []
    for sc_num in sc_numbers:
        if len(sc_num) == 14:  # 如果SC数字已经足够长，直接添加
            valid_pairs.append(sc_num)
        else:
            for pure_num in pure_numbers:
                tmp = sc_num + pure_num
                if len(tmp) == 14:
                    valid_pairs.append(tmp)
                    # 可选：从pure_numbers中移除已使用的数字，以避免重复使用
                    pure_numbers.remove(pure_num)
                    break  # 找到一组后停止内层循环

    return valid_pairs


def extract_producer(boarding_boxes: list):
    """
    从boarding_boxes中提取生产商信息
    Args:
        boarding_boxes:

    Returns:
        producer list
    """
    if (not boarding_boxes
            or not isinstance(boarding_boxes, list)
            or len(boarding_boxes) == 0
            or not boarding_boxes[0].get('words')):
        return []

    # 定义用于检测特殊字符的函数（这里简单认为是非汉字字符）
    def is_special_char(char):
        return not '\u4e00' <= char <= '\u9fff'  # 汉字字符的Unicode范围

    # 定义生产商的关键字
    producer_keys = {'生产商', '生产厂家', '生产单位', '生产者', '制造商', '制造单位', '委托方', "委托单位"}

    # 用于记录结果的列表
    extracted_data = []

    # 遍历每个box
    for box in boarding_boxes:
        if any(key in box['words'] for key in producer_keys):
            word = box['words']

            i = 0
            while i < len(word):
                # 找到“生产商”的位置
                if word[i:i + 3] in producer_keys:
                    # 跳过“生产商”这三个字
                    i += 3

                    # 寻找紧随其后的第一个汉字
                    while i < len(word) and is_special_char(word[i]):
                        i += 1

                    if i < len(word) and not is_special_char(word[i]):
                        # 开始记录汉字
                        start_i = i

                        # 寻找紧随汉字后的第一个特殊字符
                        while i < len(word) and not is_special_char(word[i]):
                            i += 1

                            # 提取并记录汉字字符串
                        if start_i < i:
                            extracted_data.append(word[start_i:i])
                else:
                    # 如果没有找到“生产商”，则继续遍历
                    i += 1

    return extracted_data


def extract_expiration_time(boarding_boxes: list):
    """
        从boarding_boxes中提取生产日期信息
        Args:
            boarding_boxes:

        Returns:
            producer list
        """
    if (not boarding_boxes
            or not isinstance(boarding_boxes, list)
            or len(boarding_boxes) == 0
            or not boarding_boxes[0].get('words')):
        return []
    # 拼接所有words为一个长字符串
    long_string = ''.join(box['words'] for box in boarding_boxes)

    # 定义用于检测特殊字符的函数（这里简单认为是非汉字字符）
    def is_special_char(char):
        return not (('\u4e00' <= char <= '\u9fff') or ('0' <= char <= '9'))  # 汉字和阿拉伯字符的Unicode范围

    # 用于记录结果的列表
    extracted_data = []

    # 定义结束标识
    end_markers = {'年', '月', '日', '天', '时', '分', '秒'}

    # 遍历长字符串
    i = 0
    while i < len(long_string):
        # 找到“生产商”的位置
        if long_string[i:i + 3] == '保质期':

            # 跳过“生产商”这三个字
            i += 3

            # 寻找紧随其后的第一个有效字符
            while i < len(long_string) and is_special_char(long_string[i]):
                i += 1

            if i < len(long_string) and not is_special_char(long_string[i]):
                # 开始记录汉字
                start_i = i
                # 取最近的12个字符找到最后的一个结束标识
                find_end = False
                for end_i in range(i + 10, i, -1):
                    if long_string[end_i] in end_markers:
                        i = end_i + 1
                        find_end = True
                        break
                # 如果没有找到结束字符，则找有效字符
                if not find_end:
                    while i < len(long_string) and not is_special_char(long_string[i]):
                        i += 1
                # 提取并记录汉字字符串
                if start_i < i:
                    extracted_data.append(long_string[start_i:i])
        else:
            # 如果没有找到“生产商”，则继续遍历
            i += 1

    return extracted_data


if __name__ == '__main__':
    boarding_boxes = [
        {'words': 'Hello SC123456789012 world'},
        {'words': 'This is 134 and then 58'},
        {'words': 'No SC here, just 901234567'},
        {'words': 'Another SC123 with 4567'}
    ]
    print(extract_sc_license(boarding_boxes))

    boarding_boxes = [
        {'words': '苏俄u护发素的远射得分吉萨大'},
        {'words': '无关信息'},
        {'words': '生产商ss数据撒旦发生ll生产商   又一组数据789'},
        {'words': '生产商:但这里没有汉字数据'},
    ]
    print(extract_producer(boarding_boxes))

    boarding_boxes = [
        {'words': '苏俄u护发素的远射得分吉萨大'},
        {'words': '无关信息'},
        {'words': '保质期：2年零3个月'},
        {'words': '生产商:但这里没有汉字数据'},
    ]
    print(extract_expiration_time(boarding_boxes))
