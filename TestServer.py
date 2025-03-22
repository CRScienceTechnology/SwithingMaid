class MQTTClient(QMainWindow):
    def __init__(self):
        # 更新MQTT客户端实例的创建方式
        self.client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
        # 设置当客户端连接到MQTT代理时的回调函数  
        self.client.on_connect = self.on_connect  
        # 设置当客户端接收到消息时的回调函数
        self.client.on_message = self.on_message  


    def on_connect(self, client, userdata, flags, rc, properties=None):
        """
        当客户端与MQTT代理成功建立连接时调用的回调函数。
    
        参数:
        - client: 客户端实例，用于操作MQTT客户端。
        - userdata: 用户定义的数据，可以在客户端初始化时指定。
        - flags: 连接应答的标志位，表示连接的属性。
        - rc: 连接结果代码，表示连接成功与否。
        - properties: 连接的属性（MQTTv5新增参数）。
    
        此函数没有返回值。
        """
        # 在文本编辑区域追加显示连接结果代码
        self.text_edit.append(f"Connected with result code {rc}")