import requests
from sekiro import SekiroServer
import sys
import json
from fake_useragent import UserAgent

class ZhongSY:
    def __init__(self):
        # 注册一个sekiro服务group
        self.sekiro_server = SekiroServer('zhongshiyou', 'xxxxxxxx')
        self.url = 'https://www.cnpcbidding.com/cms/pmsbidInfo/listPageOut'
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Content-Type': 'application/json;charsetset=UTF-8',
            'Referer': 'https://www.cnpcbidding.com/html/1/index.html',
        }
        self.fake_ua = UserAgent()

    # 调用服务器加密
    def encrypt_message(self,data):
        """与js注入文件对应，传入页面数据，返回AES加密的page数据、RSA加密的AES_key数据"""
        result = self.sekiro_server.get_data('my_encrypt', params=data).json()
        try:
            result_data = result['data']
        except Exception as e:
            print("KeyError:", e, '=>', result)
            sys.exit()
        return result_data

    # 调用服务器解密
    def decrypt_message(self,data):
        result = self.sekiro_server.get_data('my_decrypt', params=data, method='post').json()
        try:
            result_data = result['data']
        except Exception as e:
            print("KeyError:", e, '=>', result)
            sys.exit()
        return result_data

    def xhr_request(self,request_data,encrypted):
        self.headers['User-Agent'] = self.fake_ua.random
        json_dict = {
            'requestData': request_data,
            'encrypted': encrypted,
        }
        # print(json_dict)
        response = requests.post(self.url, headers=self.headers,json=json_dict, verify=False)
        response_json = response.json()
        return response_json

    def save_data(self,data):
        """这里存储形式就不写了"""
        print(data)

    def run(self):
        for page in range(1,10):
            data = {'page': page}
            # 向sekiro服务器请求加密请求数据用于请求目标网址
            print('请求加密数据')
            encrypt_result = self.encrypt_message(data)
            # 请求数据加密key
            encrypted = encrypt_result['key_data']
            # 请求数据密文
            request_data = encrypt_result['page_data']
            # 向目标网址发送请求，获取响应，包含'encrypted'加密的key，'requestData'加密的目标数据
            print('请求目标网址  第%s页' % page)
            response_json = self.xhr_request(request_data,encrypted)
            response_encrypted = response_json['encrypted']
            response_data = response_json['requestData']
            encrypt_response = {
                'encrypted': response_encrypted,
                'request_data': response_data,
            }
            # 向sekiro服务器发送加密响应，获取解密后的数据
            result = self.decrypt_message(encrypt_response)
            print('第%s页完成解析' % page)
            information = result['dataStr']
            information = json.loads(information)
            self.save_data(information['list'])
            # raise


if __name__ == '__main__':
    spider = ZhongSY()
    spider.run()

