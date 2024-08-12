#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/8/11 16:54
# @function: the script is used to do something.
# @version : V1

import utils


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
        sc_license = utils.extract_sc_license(self.boarding_boxes)
        producer = utils.extract_producer(self.boarding_boxes)
        expiration_time = utils.extract_expiration_time(self.boarding_boxes)
        return {"sc_license": sc_license, "producer": producer, "expiration_time": expiration_time}
