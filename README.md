# exhibition
通过网页管理多种代理软件的进程管理服务, 来实现混合多种协议的桥接模式服务。


```shell
# 需要 python 3.10 以上版本的环境
$ pip install exhibition-proxy
```


### 如何工作
此项目不创造新的通信协议，需要在系统中安装代理软件并添加其路径到服务设置中。
此项目的服务将控制环境中的代理软件进行组合(通常以socks5协议做中转进程)， 再由特定代理软件(通常是v2ray进程)作为外露服务提供最终服务。
即此项目主要工作是管理两套代理软件进程：一组专为远程节点联通的内部代理进程，和一组连接多个内部代理进程的最终服务进程。
由于会根据节点数量多开进程，这种运作方式比较费设备上的资源。

```text
$ exhibition  --help
usage: exhibition [-h] [--host HOST] [--port PORT] [--loglevel LOGLEVEL] [--accesslog]

exhibition

options:
  -h, --help           show this help message and exit
  --host HOST          web服务监听地址，默认0.0.0.0
  --port PORT          web服务监听端口，默认8080
  --loglevel LOGLEVEL  日志等级，默认INFO
  --accesslog          是否打印web服务器的访问日志
```


### 支持的软件

* shadowsocks
* v2ray
* xray

