## 基于sekiro的web注入
以某招投标网为例，实践了sekiro框架实现AES，RSA的加解密调用；   
sekiro官方项目地址：https://github.com/virjar/sekiro   
### 关于https协议的sekiro配置
对于https协议的网址，浏览器会禁止ws的连接，需要使用wss协议；
如何在服务器配置wss，查看sekiro_wss.md文件
### js注入
官方文档地址：https://github.com/virjar/sekiro/blob/master/open-source-doc/README.md   
代码注入：以下为官方demo   
```html
<script type="text/javascript" src="http://file.virjar.com/sekiro_web_client.js?_=123"></script>

<script type="text/javascript">
    var client = new SekiroClient("wss://sekiro.virjar.com/websocket?group=ws-group&clientId=testClient");
    client.registerAction("clientTime",function(request, resolve,reject ){
        resolve(""+new Date());
    })
</script>
```  
本案例将demo中链接的js代码拉取了下来，自定义了一个client，对应两个action，详见js_injection.js     
js注入可以通过中间人替换、油猴脚本注入、手动控制台注入；   
使用sekiro框架，需要注意js的注入位置，需要满足能调用需求参数、方法的条件，本案例中在加解密位置断点注入，可以实现AES，RSA的部分参数和方法调用。   
### 服务通信
js文件与服务的ws连接是走5603端口，本案例中使用nginx配置ssl，实际发起的wss连接走5605端口由nginx转发到5603端口；   
蜘蛛程序与sekiro服务的连接走5601异步端口，支持get请求；5602端口支持get、post请求；   
本案例中加密服务走的5601 get请求，而解密服务传输数据较大，走的5602 post请求。   
**在与js文件之间传输数据的时候不要用data作为key，会与服务的data冲突，导致其他参数不能传输**
> 备注: 目前 Sekiro 存在四个保留参数，业务放不能使用这几个作为参数的 key，包括:group,action,clientId,invoke_timeOut
### sekiro服务封装
针对web端，对sekiro服务进行基于requests的请求封装；   
使用时生成一个server类，调用类的get_data方法完成对sekiro服务的请求，包含get或post；   
方便其他项目代码复用；

