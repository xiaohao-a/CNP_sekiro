## 如何让服务器支持ssl WebSocket
在sekiro框架时，如果要注入的是https协议网址：
> 如果你要注入的网页是 https 的，那么直接通过我们的 websocket 服务会被浏览器拦截。

会导致wss连接服务失败（wss是基于ssl的ws协议）
## sekiro端口
```
#tomcat 占用端口
server.port=5602
#长链接服务占用端口
natServerPort=5600
# 异步http占用端口
natHttpServerPort=5601
# websocket占用端口
webSocketServerPort=5603
```

### 如何实现wss
- 一种方案：用nginx配置ssl，转发wss到ws的端口
### 如何配置ssl
1. 生成ssl证书，考虑仅仅是自用，就不去购买证书了：   
   - 生成服务器私钥，nginx配置要使用2048长度的私钥：    
   openssl genrsa -out server.key 2048   
   - 创建服务器证书的申请文件：   
   openssl req -new -key server.key -out server.csr      
   - 生成服务器的证书：    
   openssl x509 -req -days 3650 -sha1 -extensions v3_req -CA root.crt -CAkey root.key -CAserial root.srl -CAcreateserial -in server.csr -out server.crt
   - 注意：在创建申请证书文件的时候：
   > Country Name (2 letter code) [AU]:CN ← 国家代号，中国输入CN    
    State or Province Name (full name) [Some-State]:BeiJing ← 省的全名，拼音    
    Locality Name (eg, city) []:BeiJing ← 市的全名，拼音    
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:MyCompany Corp. ← 公司英文名    
    Organizational Unit Name (eg, section) []: ← 可以不输入    
    Common Name (eg, YOUR name) []: ← 此时不输入    
    Email Address []:admin@mycompany.com ← 电子邮箱，可随意填   

   > Please enter the following ‘extra’ attributes 
    to be sent with your certificate request    
    A challenge password []: ← 可以不输入   
    An optional company name []: ← 可以不输入    
   - 需要在服器上使用的是 key文件和crt文件
2. 配置nginx
   - 在/etc/nginx/conf.d下创建新的文件ssl.conf   
   - 配置ssl.conf文件内容：
   ```shell
        server
        {
            listen 5605 ssl;    # sekiro服务占用了5600-5603端口，在js注入的wss要和这里配置的端口一样
            # server_name 域名;  # 我的服务器没有配置域名
            
            ssl_certificate /etc/nginx/conf.d/server.crt;
            ssl_certificate_key /etc/nginx/conf.d/server.key;
            
            location / {   
            proxy_pass http://127.0.0.1:5603/;  # 通过配置端口指向sekiro服务的默认5603端口
            proxy_http_version 1.1;
            proxy_read_timeout 600s;            # nginx默认配置的websocket协议会在60s没有数据传输时候断掉，这里修改为10分钟
            proxy_set_header Upgrade $http_upgrade;    
            proxy_set_header Connection "Upgrade";    
            proxy_set_header X-real-ip $remote_addr;  
            proxy_set_header X-Forwarded-For $remote_addr;
            }
        }
   ```  
 3. 配置完后检查语法：nginx -t 重启nginx：service nginx restart
 
 4. 启动浏览器连接刚刚自己配置的服务器端口，5605    
  当然也可以配置成浏览器默认的80端口，这个随意  
  访问https://服务器ip地址：5605，由于证书没有认证，需要手动允许访问，缺浏览器有返回结果后就可以开始js注入了。
  当然，用浏览器直接访问sekiro服务会返回400 Bad Request，这表示https协议走通了。   
 
 5. 将js代码注入目标网址，就可以实现各种骚操作了，注意js文件的链接sekiro服务地址要变成   
 "wss://服务器ip:5605/websocket?group=xxxx&clientId=xxxx"，当然对于http还是走ws协议5603端口就好。
 
 注意：修改js注入文件后要刷新网页后再注入