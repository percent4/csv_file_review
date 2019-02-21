# -*- coding: utf-8 -*-

import xlrd
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

#定义端口为12306
define("port", default=12306, help="run on the given port", type=int)

class UploadFileHandler(tornado.web.RequestHandler):
    # get函数
    def get(self):
        self.render('upload.html')

    # post函数
    def post(self):
        # 文件的存放路径
        upload_path = os.path.join(os.path.dirname(__file__), 'files')
        # 提取表单中‘name’为‘file’的文件元数据
        file_metas = self.request.files['file']
        for meta in file_metas:
            filename = meta['filename']
            filepath = os.path.join(upload_path, filename)
            # 有些文件需要已二进制的形式存储，实际中可以更改
            with open(filepath, 'wb') as up:
                up.write(meta['body'])
            self.write("<br><br>")
            self.write('<p>上传%s成功!</p>' % filename)
            self.write('<p><a href="/file_review"><button>查看全部文件</button></a></p>')

class FileReviewHandler(tornado.web.RequestHandler):
    def get(self):
        # 文件的存放路径
        upload_path = os.path.join(os.path.dirname(__file__), 'files')
        files = os.listdir(upload_path)
        for file in files:
            if os.path.isdir(file):
                files.remove(file)

        self.render('fileReview.html', files=files)

class DataReviewHandler(tornado.web.RequestHandler):

    def get(self):
        filename = self.get_argument('file')
        print(filename)
        # 文件的存放路径
        upload_path = os.path.join(os.path.dirname(__file__), 'files')
        file_path = os.path.join(upload_path, filename)

        if filename.endswith('.csv'):
            with open(file_path, "r") as f:
                data = f.readlines()
            data = [line.strip().split(',') for line in data]

        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            tables = xlrd.open_workbook(file_path)
            table = tables.sheets()[0] # 第一张表格
            nrows = table.nrows

            # 循环行列表数据
            data = []
            for i in range(nrows):
                data.append(table.row_values(i))

        else:
            data = []

        self.render('dataReview.html', data=data)

# 主函数
def main():

    # 开启tornado服务
    tornado.options.parse_command_line()
    # 定义app
    app = tornado.web.Application(
            handlers=[(r'/file', UploadFileHandler),
                      (r'/file_review', FileReviewHandler),
                      (r'/data', DataReviewHandler)
                      ],    # 网页路径控制
            template_path=os.path.join(os.path.dirname(__file__), "templates"), # 模板路径
            static_path=os.path.join(os.path.dirname(__file__), "static"),  # 配置静态文件路径
          )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

main()