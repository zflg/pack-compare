#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/11 16:54
# @function: the script is used to do something.
# @version : V1

import utils


def is_special_char(char):
    return not (
            ('\u4e00' <= char <= '\u9fff')  # 汉字字符的Unicode范围
            or ('0' <= char <= '9')
            or ('a' <= char <= 'z')
            or ('A' <= char <= 'Z')
            or char in ['(', ")", '（', "）"]
    )


class FoodPackInfo:

    def __init__(self, sc_license: list, producer: str, expiration_time: str):
        self.sc_license = sc_license
        self.producer = producer
        self.expiration_time = expiration_time

    def __str__(self):
        return f"FoodPackInfo(sc_license={self.sc_license}, producer={self.producer}, expiration_time={self.expiration_time})"


class FoodPackKIE:

    def __init__(self, boarding_boxes: list):
        self.boarding_boxes = boarding_boxes

    def run(self):
        """
        Run the KIE model.
        当前自己写逻辑来提取食品包装信息，后期可以使用语言模型来提取
        Returns:
        """
        sc_license = self.extract_sc_license()
        producer = self.extract_producer()
        expiration_time = self.extract_expiration_time()
        return {"sc_license": sc_license, "producer": producer, "expiration_time": expiration_time}

    def extract_sc_license(self):
        """
        从boarding_boxes中提取SC证书号，可能提取多个，主要处理换行的情况
        Returns:
            sc license list
        """
        boarding_boxes = self.boarding_boxes
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
            sc_matches = re.findall(r'SC(\d{1,14})', word)
            for match in sc_matches:
                sc_numbers.append('SC' + match)

            # 提取纯数字
            number_matches = re.findall(r'\b\d+\b', word)  # 使用\b确保匹配的是完整的单词（即数字）
            for match in number_matches:
                pure_numbers.append(match)

        # 尝试拼接SC数字和纯数字以形成长度为14的字符串
        valid_pairs = []
        for sc_num in sc_numbers:
            if len(sc_num) == 16:  # 如果SC数字已经足够长，直接添加
                valid_pairs.append(sc_num)
            else:
                for pure_num in pure_numbers:
                    tmp = sc_num + pure_num
                    if len(tmp) == 16:
                        valid_pairs.append(tmp)
                        # 可选：从pure_numbers中移除已使用的数字，以避免重复使用
                        pure_numbers.remove(pure_num)
                        break  # 找到一组后停止内层循环

        return valid_pairs

    def extract_producer(self):
        """
        从boarding_boxes中提取生产商信息
        Returns:
            producer list
        """
        boarding_boxes = self.boarding_boxes
        if (not boarding_boxes
                or not isinstance(boarding_boxes, list)
                or len(boarding_boxes) == 0
                or not boarding_boxes[0].get('words')):
            return []

        # 定义结束标识
        end_markers = {'公司'}

        # 定义生产商的关键字
        producer_keys = {'生产商', '生产厂家', '生产单位', '生产企业', '生产者', '制造商', '制造单位', '委托方', '委托单位', '委托生产方', '委托生产单位', }

        # 用于记录结果的列表
        extracted_data = []

        # 遍历每个box
        for index, box in enumerate(boarding_boxes):
            for key in producer_keys:
                if key in box['words']:
                    # 如果当前box不是最后一个box，则将当前box和下一个box合并
                    if index < len(boarding_boxes) - 1:
                        word = box['words'] + boarding_boxes[index + 1]['words']
                    else:
                        word = box['words']
                    # 找到key在word中的位置并跳过key
                    i = word.index(key) + len(key)
                    # 寻找紧随其后的第一个有效字符
                    while i < len(word) and is_special_char(word[i]):
                        i += 1
                    # 开始记录有效字符
                    start_i = i
                    # 寻找紧随有效字符后的第一个特殊字符
                    while i < len(word) and not is_special_char(word[i]) and word[i - 2:i] not in end_markers:
                        i += 1
                    # 提取并记录有效字符串
                    if start_i < i:
                        extracted_data.append(word[start_i:i])

        return extracted_data

    def extract_expiration_time(self):
        """
        从boarding_boxes中提取生产日期信息
        Returns:
            producer list
        """
        boarding_boxes = self.boarding_boxes
        if (not boarding_boxes
                or not isinstance(boarding_boxes, list)
                or len(boarding_boxes) == 0
                or not boarding_boxes[0].get('words')):
            return []

        # 用于记录结果的列表
        extracted_data = []

        # 定义结束标识
        end_markers = {'年', '月', '日', '天', '时', '分', '秒'}

        # 定义保质期关键字
        expiration_time_keys = {'保质期', '保质日期', '保质时间', '有效期', '有效日期', '有效时间'}

        # 遍历每个box
        for box in boarding_boxes:
            for key in expiration_time_keys:
                if key in box['words']:
                    word = box['words'][box['words'].find(key):]
                    word_len = len(word)
                    # 首先截断生产日期这种干扰
                    position = word.find('生产日期')
                    if position != -1:
                        word_len = position
                    # 找到key在word中的位置并跳过key
                    i = word.index(key) + len(key)
                    # 寻找紧随其后的第一个有效字符
                    while i < word_len and is_special_char(word[i]):
                        i += 1
                    # 开始记录有效字符
                    start_i = i
                    # 寻找紧随有效字符后的第一个特殊字符
                    while i < word_len and not is_special_char(word[i]):
                        i += 1
                    # 提取并记录有效字符串
                    if start_i < i:
                        # 查看最后一个字符是否是结束标识，不是则取最近的8个字符找结束标识
                        if word[i - 1] not in end_markers:
                            for end_i in range(start_i + 8, start_i, -1):
                                if word[end_i] in end_markers:
                                    i = end_i + 1
                                    break
                        extracted_data.append(word[start_i:i])

        return extracted_data


class ScreenShotKie:

    def __init__(self, boarding_boxes: list):
        self.boarding_boxes = boarding_boxes

    def run(self):
        """
        Run the KIE model.
        当前自己写逻辑来提取食品包装信息，后期可以使用语言模型来提取
        Returns:
        """
        sc_license = self.extract_sc_license()
        sample_name = self.extract_sample_name()
        produce_date = self.extract_produce_date()
        bz_license = self.extract_bz_license()

        return {"sc_license": sc_license, "sample_name": sample_name, "produce_date": produce_date, "bz_license": bz_license}

    def _extract_next_box_inline(self, key):
        """
        从boarding_boxes中提取下一个box，但是下一个box如果换行，则返回None
        Args:
            key:
            index:
            boarding_boxes:

        Returns:
            next box
        """
        boarding_boxes = self.boarding_boxes
        if (not boarding_boxes
                or not isinstance(boarding_boxes, list)
                or len(boarding_boxes) == 0
                or not boarding_boxes[0].get('words')):
            return None
        # 找到包含关键字[key]的box，并返回它的下一个box，但是下一个box如果换行，则返回None
        for box in boarding_boxes:
            if key in box['words']:
                cur_top_y = box['location']['top']
                cur_below_y = box['location']['top'] + box['location']['height']
                cur_right_x = box['location']['left'] + box['location']['width']
                # 遍历所有box，找到下一个box
                for next_box in boarding_boxes:
                    if next_box == box:
                        continue
                    next_top_y = next_box['location']['top']
                    next_below_y = next_box['location']['top'] + next_box['location']['height']
                    next_left_x = next_box['location']['left']
                    # inline的判断，next box的左上角高于当前box的左下角，next box的右上角低于当前box的右下角，x轴无交集
                    if next_top_y <= cur_below_y and next_below_y >= cur_top_y and next_left_x > cur_right_x:
                        return next_box['words']
        return None

    def extract_sc_license(self):
        """
        从boarding_boxes中提取SC证书号，可能提取多个，主要处理换行的情况
        Returns:
            sc license
        """
        return self._extract_next_box_inline("SC号")

    def extract_sample_name(self):
        """
        从boarding_boxes中提取样品名称信息
        Returns:
            sample name
        """
        return self._extract_next_box_inline("样本名称")

    def extract_produce_date(self):
        """
        从boarding_boxes中提取生产日期信息
        Returns:
            produce date
        """
        return self._extract_next_box_inline("生产日期")

    def extract_bz_license(self):
        """
        从boarding_boxes中提取BZ证书号信息
        Returns:
            bz license
        """
        return self._extract_next_box_inline("营业执照号")


if __name__ == '__main__':
    kie = FoodPackKIE([
        {'words': 'Hello SC12345678901234 world'},
        {'words': 'This is 134 and then 58'},
        {'words': 'No SC here, just 90123456789'},
        {'words': 'Another SC123 with 4567'}
    ])
    print(kie.extract_sc_license())

    kie = FoodPackKIE([
        {'words': '苏俄u护发素的远射得分吉萨大'},
        {'words': '无关信息'},
        {'words': '生产商：数据撒旦发生ll生产商   又一组数据789'},
        {'words': '浙江生产单位:但这里没有汉字数据'},
        {'words': '有限公司保质日期：12个月'},
    ])
    print(kie.extract_producer())

    kie = FoodPackKIE([
        {'words': '苏俄u护发素的远射得分吉萨大'},
        {'words': '无关信息'},
        {'words': '保质期：12个月零一日生产日期：2024年8月11日'},
        {'words': '有限公司保质日期：12个月'},
        {'words': '生产日期：（年/月/日）'},
        {'words': '保质期：12个月生产日期标于瓶盖或者瓶身'},
        {'words': '生产日期：见瓶体（或瓶盖）保质期：18个月'},
    ])
    print(kie.extract_expiration_time())

    prediction = [{'probability': {'average': 0.9992135763, 'min': 0.9927974343, 'variance': 4.576815172e-06}, 'words': '10:239月26日',
                   'location': {'top': 11, 'left': 47, 'width': 193, 'height': 32}},
                  {'probability': {'average': 0.9999781847, 'min': 0.9999598265, 'variance': 3.370246304e-10}, 'words': '周四',
                   'location': {'top': 12, 'left': 251, 'width': 59, 'height': 31}},
                  {'probability': {'average': 0.9999492764, 'min': 0.9999064207, 'variance': 1.836614416e-09}, 'words': '45',
                   'location': {'top': 20, 'left': 1481, 'width': 25, 'height': 16}},
                  {'probability': {'average': 0.9994804263, 'min': 0.9994804263, 'variance': 0}, 'words': '<',
                   'location': {'top': 86, 'left': 33, 'width': 28, 'height': 43}},
                  {'probability': {'average': 0.9994714856, 'min': 0.9991490841, 'variance': 7.827444648e-08}, 'words': '样品填报',
                   'location': {'top': 87, 'left': 722, 'width': 152, 'height': 41}},
                  {'probability': {'average': 0.9997881055, 'min': 0.99935776, 'variance': 6.241887718e-08}, 'words': 'SC号：',
                   'location': {'top': 306, 'left': 71, 'width': 94, 'height': 36}},
                  {'probability': {'average': 0.9999607801, 'min': 0.9998807907, 'variance': 1.078768186e-09}, 'words': 'SC10634122207025',
                   'location': {'top': 309, 'left': 411, 'width': 324, 'height': 32}},
                  {'probability': {'average': 0.9996398091, 'min': 0.9983696342, 'variance': 4.064296775e-07}, 'words': '样本名称：',
                   'location': {'top': 488, 'left': 70, 'width': 159, 'height': 38}},
                  {'probability': {'average': 0.9999471307, 'min': 0.9998549223, 'variance': 3.236055202e-09}, 'words': '云南黑咖啡固体饮料',
                   'location': {'top': 491, 'left': 410, 'width': 325, 'height': 38}},
                  {'probability': {'average': 0.999538064, 'min': 0.9977224469, 'variance': 8.240952525e-07}, 'words': '生产日期：',
                   'location': {'top': 673, 'left': 71, 'width': 157, 'height': 38}},
                  {'probability': {'average': 0.9999939203, 'min': 0.9999756813, 'variance': 6.591136664e-11}, 'words': '2024-06-02',
                   'location': {'top': 678, 'left': 409, 'width': 186, 'height': 33}},
                  {'probability': {'average': 0.9994578362, 'min': 0.9970893264, 'variance': 1.131303293e-06}, 'words': '营业执照号：',
                   'location': {'top': 857, 'left': 72, 'width': 193, 'height': 39}},
                  {'probability': {'average': 0.9661802053, 'min': 0.6637955308, 'variance': 0.01015981846}, 'words': 'GB/T 29602',
                   'location': {'top': 861, 'left': 410, 'width': 200, 'height': 38}},
                  {'probability': {'average': 0.9982610941, 'min': 0.9966891408, 'variance': 2.471130756e-06}, 'words': '清除',
                   'location': {'top': 1037, 'left': 800, 'width': 69, 'height': 33}}]
    print(ScreenShotKie(prediction).run())
