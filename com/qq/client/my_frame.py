"""定义frame窗口基类"""

import logging
import socket
import sys
import wx

logger = logging.getLogger(__name__)

#服务器
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8000

server_address = (SERVER_IP, SERVER_PORT)

#操作命令代码
COMMAND_LOGIN = 1 #登录
COMMAND_LOGOUT = 2 #下线
COMMAND_SENDMSG = 3 #发送消息
COMMAND_REFRESH = 4 #刷新好友

#初始化socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#设置socket超时1秒
client_socket.settimeout(1)

class MyFrame(wx.Frame):
    def __init__(self, title, size):
        super().__init__(parent=None, title=title, size=size,
                         style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX)

        #设置窗口居中
        self.Center()
        #设置Frame窗口内容面板
        self.contentpanel = wx.Panel(parent=self)

        ico = wx.Icon('resources/icon/hero3.png')

        #设置窗口最大最小尺寸
        self.SetSizeHints(size,size)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self):
        #退出系统
        self.Destroy()
        client_socket.close()
        sys.exit(0)