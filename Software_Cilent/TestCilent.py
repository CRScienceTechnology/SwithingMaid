import ast
import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QLabel,QMessageBox
from PyQt6.QtCore import QTimer
import paho.mqtt.client as mqtt
import json


class AutoCloseMessageBox(QMessageBox):
    """
    自定义消息框类，继承自QMessageBox。
    该类用于创建一个具有自动关闭功能的消息框。

    参数:
    - title: 消息框的标题。
    - message: 消息框显示的消息内容。
    - timeout: 消息框自动关闭前显示的时间（毫秒），默认为1000毫秒（1秒）。
    - parent: 父窗口，通常用于窗口管理，如定位和模态行为，默认为None。
    """
    def __init__(self, title, message, timeout=1000, parent=None):
        # 初始化父类构造方法
        super().__init__(parent)
        
        # 设置消息框的标题
        self.setWindowTitle(title)
        
        # 设置消息框的显示内容
        self.setText(message)
        
        # 设置消息框的标准按钮为“确定”
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # 设置默认按钮为“确定”
        self.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # 初始化定时器
        self.timer = QTimer(self)
        
        # 设置定时器的时间间隔
        self.timer.setInterval(timeout)
        
        # 将定时器的timeout信号连接到消息框的close槽，以实现自动关闭功能
        self.timer.timeout.connect(self.close)
        
        # 启动定时器
        self.timer.start()




# 定义一个继承自QMainWindow的MQTTClient类
class MQTTClient(QMainWindow):
    def __init__(self):
        """
            初始化MQTT客户端窗口。

            该构造函数首先调用父类的构造方法，然后设置窗口标题和几何形状。
            接着创建一个MQTT客户端实例，并指定连接和消息回调函数。
            最后调用initUI方法来初始化用户界面。
        """
        # 调用父类的构造方法进行初始化
        super().__init__()  
        # 设置窗口标题
        self.setWindowTitle("MQTT Client")
        # 设置窗口几何形状（位置和大小） 
        self.setGeometry(100, 100, 400, 300)  

        # 指定MQTT服务器地址
        self.broker = "47.94.167.240"
        # 设置MQTT代理端口
        self.port = 1883
        # 设置MQTT主题
        self.topic = "swithing_maid_01_state"
        # 设置初始消息内容为JSON格式
        self.message = {
            "maidcode": "01",
            "status": "on",
            "angle": 90
        }
        # 更新MQTT客户端实例的创建方式
        self.client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
        # 设置当客户端连接到MQTT代理时的回调函数  
        self.client.on_connect = self.on_connect  
        # 设置当客户端接收到消息时的回调函数
        self.client.on_message = self.recieved_message  
        # 调用初始化用户界面的方法
        self.initUI()  
        


    def initUI(self):
        # 创建一个只读的文本编辑框，用于显示消息
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        
        # 创建标签和输入框，用于输入MQTT代理地址
        self.broker_label = QLabel("Broker:", self)
        self.broker_input = QLineEdit(self)
        self.broker_input.setText(self.broker)
        
        # 创建标签和输入框，用于输入MQTT主题
        self.topic_label = QLabel("Topic:", self)
        self.topic_input = QLineEdit(self)
        self.topic_input.setText(self.topic)
        
        # 创建连接按钮，并连接到connect_to_broker方法
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_broker)
        
        # 创建订阅按钮，并连接到subscribe_topic方法
        self.subscribe_button = QPushButton("Subscribe", self)
        self.subscribe_button.clicked.connect(self.subscribe_topic)
        
        # 创建测试按钮，以0°为步进值，发送间隔为1s，发送0-180角度的消息体
        self.test_button = QPushButton("Test", self)
        self.test_button.clicked.connect(self.run_test)

        # 创建标签、输入框、按钮，用于输入消息、发送消息
        # 设置标签内容
        self.sending_message_textbox_label = QLabel("Message:", self)
        # 展示默认消息
        self.sending_message_textbox = QLineEdit(str(self.message),self)
        # 创建发布按钮，并连接到publish_message方法
        self.publish_button = QPushButton("Publish", self)
        self.publish_button.clicked.connect(self.publish_message)
        
        

        # 创建垂直布局，并将所有控件添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.broker_label)
        layout.addWidget(self.broker_input)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.topic_label)
        layout.addWidget(self.topic_input)
        layout.addWidget(self.subscribe_button)
        layout.addWidget(self.sending_message_textbox_label)
        layout.addWidget(self.sending_message_textbox)
        layout.addWidget(self.publish_button)
        layout.addWidget(self.test_button)
        
        # 创建一个容器部件，并将布局设置为该部件的布局
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def connect_to_broker(self):
        """
        连接到MQTT代理服务器。
        
        此方法使用self.broker、self.port和self.client（MQTT客户端）建立连接。
        连接参数包括代理地址、端口和保持连接的超时时间（60秒）。
        成功连接后，启动客户端的循环处理机制，并在`text_edit`文本区域
        中追加显示已连接到哪个代理服务器的信息。
        """
        # 使用获取的代理地址建立连接
        self.client.connect(self.broker, self.port, 60)
        
        # 启动客户端循环，处理网络流量
        self.client.loop_start()
        
        # 在文本区域追加显示连接信息
        self.text_edit.append(f"Connected to broker {self.broker}")

    def subscribe_topic(self):
        """
        订阅指定主题。
        
        此方法使用self.topic调用self.client.subscribe方法进行订阅。
        订阅成功后，将订阅信息追加显示到self.text_edit中。
        """
        # 使用获取的主题订阅
        self.client.subscribe(self.topic)
        
        # 在文本编辑器中更新订阅信息
        self.text_edit.append(f"Subscribed to topic {self.topic}")    

    def run_test(self):
        """

        """
        test_meassage = {
            "maidcode": "01",
            "status": "on",
            "angle": 0
        }
        topic = self.topic_input.text()
        for i in range(19):
            # 每次循环消息体角度步进10度
            test_meassage["angle"] = i * 10
            # 发布消息
            self.client.publish(topic, json.dumps(test_meassage))
            # 弹窗控件显示现在处于第几个循环
            msg_box = AutoCloseMessageBox("提示", f"第{i}次", timeout=1000, parent=self)
            msg_box.show()
            # 系统等待1秒
            QApplication.processEvents()  # 处理事件循环，避免界面冻结
            time.sleep(1)


    def publish_message(self):
        """
        发布消息到指定主题。
    
        本函数从界面组件中获取主题和消息内容，然后通过客户端发布到指定的主题。
        发布成功后，会在文本编辑器中追加显示发布的消息和主题。
        """
        # 获取主题输入框中的内容
        topic = self.topic_input.text() 
        # 获取 message_input 输入框中的内容，这里使用预设的JSON消息
        message = self.sending_message_textbox.text()
        try :
            # 尝试将字符串类型的 message 转换为格式
            message = ast.literal_eval(message)
        except json.JSONDecodeError:
            # 如果message不是有效的JSON格式，终端弹出警告
            print("Invalid JSON format. Using predefined message.")
        # 通过客户端发布消息到指定主题，使用json.dumps将message转换为JSON格式
        self.client.publish(topic, json.dumps(message))
        # 在文本编辑器中追加显示发布的消息和主题
        self.text_edit.append(f"Published message '{json.dumps(message)}' to topic {topic}")

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
    
    def recieved_message(self, client, userdata, msg):
        """
        当接收到消息时调用的回调函数。
    
        参数:
        - client: MQTT客户端实例。
        - userdata: 用户定义的数据，未使用。
        - msg: 消息数据，包含主题（topic）和负载（payload）。
    
        此函数将消息内容解码并显示在文本编辑器中，以便用户可以看到接收到的消息。
        """
        # 将接收到的消息追加到文本编辑器中，包括消息内容和主题
        self.text_edit.append(f"Received message '{msg.payload.decode()}' on topic {msg.topic}")   



if __name__ == "__main__":
    # 创建QApplication对象
    app = QApplication(sys.argv)
    # 初始化MQTTClient对象的Window实例
    window = MQTTClient()
    # 显示窗口
    window.show()
    sys.exit(app.exec())


# Repair:
# 2025.3.22：TestServer.py:31: DeprecationWarning: Callback API version 1 is deprecated, update to latest version self.client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5) Exception in thread paho-mqtt-client-
# 2025.3.22: 修复了 ESP8266 接收到的消息体类似"{\"maidcode\":\"01\",\"status\":\"on\",\"angle\":90}"的不正确形式
# 2025.3.22：将发送JSON消息的获取形式改为从控件中获取
