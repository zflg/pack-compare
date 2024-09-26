#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 坑坑
# @time    : 2024/9/25 12:14
# @function: the script is used to do something.
# @version : V1
import pack_compare_routing
import dup_check_routing
import logging

from flask import Flask
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.register_blueprint(pack_compare_routing.pack_compare_bp)
app.register_blueprint(dup_check_routing.dup_check_bp)

CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有源的跨域请求

if __name__ == '__main__':
    # 运行Flask应用，监听8000端口
    app.run(port=8000, debug=True)
