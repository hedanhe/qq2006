import datetime
import threading
import json
from com.qq.client.my_frame import *
import time

"""聊天窗口"""
class CharFrame(MyFrame):

    def __init__(self, friendsframe, user, friend):
        super().__init__(title="", size=(450, 400))

        self.friendsframe = friendsframe
        self.user = user
        self.friend = friend

        title = '{0}与{1}聊天中……'.format(user['user_name'], friend['user_name'])
        self.SetTitle(title)

        #创建敞开文本消息输入框--wx.TE_MULTILINE多行文本
        self.seemsg_tx = wx.TextCtrl(self.contentpanel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        #底部发送消息面板
        bottompanle = wx.Panel(self.contentpanel, style=wx.DOUBLE_BORDER)

        bottombox = wx.BoxSizer()

        #创建发送消息文本输入控件
        self.sendmsg_tc = wx.TextCtrl(bottompanle)
        # self.sendmsg_tc.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT,
        #                                 wx.FONTSTYLE_NORMAL,
        #                                 wx.FONTWEIGHT_NORMAL))

        #创建发送消息按钮
        sendmsg_btn = wx.Button(bottompanle, label='发送')
        self.Bind(wx.EVT_BUTTON, self.on_click, sendmsg_btn)

        bottombox.Add(self.sendmsg_tc, 5, wx.CENTER | wx.ALL | wx.EXPAND, border=5)
        bottombox.Add(sendmsg_btn, 1, wx.CENTER | wx.ALL | wx.EXPAND, border=5)

        bottompanle.SetSizer(bottombox)

        #创建整体布局
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.seemsg_tx, 5, wx.CENTER| wx.ALL | wx.EXPAND, border=5)
        box.Add(bottompanle, 1, wx.CENTER | wx.ALL | wx.EXPAND, border=5)

        #初始化日志
        self.contentpanel.SetSizer(box)

        #消息日志
        self.msglog = ''

        self.isrunning = True
        self.t1 = threading.Thread(target=self.thread_body)
        self.t1.start()

    def on_click(self, event):
        """{"receive_user_id": "222"，
            "message": "你好吗"，
            “user_id”: "111"
            "command": 3
        }"""

        now = datetime.datetime.today()
        strnow = now.strftime('%Y-%m-%d %H:%M%S' )
        json_obj = {}
        json_obj["receive_user_id"] = self.friend["user_id"]
        json_obj["message"] = self.sendmsg_tc.GetValue()
        json_obj["user_id"] = self.user["user_id"]
        json_obj["command"] = COMMAND_SENDMSG

        if self.sendmsg_tc.GetValue():
            print("发送消息到服务器")
            # json编码
            json_str = json.dumps(json_obj)
            # 给服务器发送数据
            client_socket.sendto(json_str.encode(), server_address)

            now = datetime.datetime.today()
            strnow = now.strftime('%Y-%m-%d %H:%M:%S')

            message = json_obj["message"]
            log = '{0}\n您对{1}说： {2}\n'.format(strnow, self.friend["user_name"], message)
            self.msglog += log

            self.sendmsg_tc.SetValue("")
            self.seemsg_tx.SetValue(self.msglog)
            # 光标显示在最后一行
            self.seemsg_tx.SetInsertionPointEnd()



    # 线程体方法
    def thread_body(self):
        while self.isrunning:
            try:
                # 从服务器接收数据
                json_data, _ = client_socket.recvfrom(1024)
                # json解码
                json_obj = json.loads(json_data.decode())
                print("json_obj", json_obj)
                logger.info("线程刷新好友从服务器接收数据：'{0}'".format(json_obj))
                cmd = json_obj['command']
                print("从服务器接收数据***************************", cmd)

                if cmd is not None:
                    if cmd == COMMAND_REFRESH:
                        userid_list = json_obj['OnlineUserlist']
                        if len(userid_list) > 0:
                            # 刷新好友列表
                            print("刷新好友列表")
                            self.friendsframe.refreshfriendlist(userid_list)

                    elif cmd == COMMAND_SENDMSG:
                        print("收到服务器发过来消息")
                        now = datetime.datetime.today()
                        strnow = now.strftime('%Y-%m-%d %H:%M:%S')

                        message = json_obj["message"]
                        log = '{0}\n{1}对您说： {2}\n'.format(strnow, self.friend["user_name"], message)
                        self.msglog += log

                        self.seemsg_tx.SetValue(self.msglog)
                        #光标显示在最后一行
                        self.seemsg_tx.SetInsertionPointEnd()


            except Exception:
                continue
            time.sleep(2)

    def OnClose(self, event):
        #停止线程
        self.isrunning = False
        self.t1.join()
        self.Hide()

        #重启好友列表窗口中的子线程
        self.friendsframe.resetthread()