import requests

class SekiroServer:
    def __init__(self, name, addr='127.0.0.1'):
        """
        封装向sekiro服务端的请求操作，对象方法：get_data
        :param name: 自定义请求服务分类（group）名称
        :param addr: sekiro服务的ip地址
        """
        self.group = str(name)
        self.addr = str(addr)

    def get_data(self,action='action',params=None,method='get'):
        """
        向sekiro服务发送HTTP请求，实现与浏览器sekiro客户端通信
        :param action: 自定义请求动作（服务端查找对应的动作返回结果）
        :param params: dict类型的自定义参数，注入的js代码可以调用
        :param method: 'get' or 'post'，参数太复杂或太大建议使用post
        :return: 返回注入js代码的返回值
        """
        # sekiro服务同一个group下可以有多个action
        param_dict = {'group': self.group,'action': action}
        if params:
            if type(params) is not dict:
                raise TypeError("Parameter type error: 'params' should be dict")
            param_dict.update(params)
        url = self.__create_url(method)
        response = requests.get(url, params=param_dict)
        return response

    def __create_url(self,method):
        """ 根据请求模式，生成服务请求地址 """
        # 传输参数大小超出4k建议用post方法，实测数据太大后get方法不能正常通讯
        if method == 'get':
            # get请求走服务器默认异步通道
            url = 'http://' + self.addr + ':5601/asyncInvoke'
        elif method == 'post':
            # post请求需要走5602端口
            url = 'http://' + self.addr + ':5602/invoke'
        else:
            raise ValueError("Parameter value error: value of 'method' should be 'get' or 'post'")
        return url
