

"""好友列表窗口"""
import datetime
import threading
from wx.lib import scrolledpanel
import json
import time

from com.qq.client.chat_frame import CharFrame
from com.qq.client.my_frame import *


class FriendsFrame(MyFrame):
    def __init__(self, json_obj):
        super().__init__(title="我的好友", size=(260, 600))

        self.chatFrame = None

        #用户信息
        self.user = json_obj["user"]
        #好友列表
        self.friends = json_obj['friends']
        #好友控件列表...便于刷新好友列表时使用
        self.friendctrols = []

        usericonfile = 'resources/images/{0}.jpg'.format(self.user['user_icon'])
        # 用户头像
        usericon = wx.Image(usericonfile, wx.BITMAP_TYPE_JPEG)
        usericon.Rescale(80, 80)
        user_img = usericon.ConvertToBitmap()
        # 顶部面板
        toppanle = wx.Panel(self.contentpanel)
        usericon_sbitmap = wx.StaticBitmap(toppanle, -1, user_img)
        #静态文本水平剧中
        username_st = wx.StaticText(toppanle, wx.ALIGN_CENTER_HORIZONTAL)
        username_st.SetLabel(self.user["user_name"])
        #顶部Box布局管理
        topbox = wx.BoxSizer(wx.VERTICAL)
        #加空白
        topbox.AddSpacer(15)
        topbox.Add(usericon_sbitmap, 1, wx.CENTER)
        topbox.AddSpacer(5)
        topbox.Add(username_st, 1, wx.CENTER)

        toppanle.SetSizer(topbox)

        #好友列表面板
        panle = scrolledpanel.ScrolledPanel(self.contentpanel, -1, size=(260, 1000), style=wx.DOUBLE_BORDER)

        gridsizer = wx.GridSizer(cols=1, rows=20, gap=(1,1))
        if len(self.friends) >20:
            gridsizer = wx.GridSizer(cols=1, rows=len(self.friends), gap=(1,1))

        #添加好友到控制面板
        for index, friend in enumerate(self.friends):
            print(index,friend)
            friendpanel = wx.Panel(panle, id=index)

            fdname_st = wx.StaticText(friendpanel, id=index, style=wx.ALIGN_CENTER_HORIZONTAL)
            fdname_st.SetLabel(friend['user_name'])
            fdqq_st = wx.StaticText(friendpanel, id=index, style=wx.ALIGN_CENTER_HORIZONTAL)
            fdqq_st.SetLabel(friend['user_id'])

            path = 'resources/images/{0}.jpg'.format(friend['user_icon'])
            icon = wx.Image(path, wx.BITMAP_TYPE_JPEG)
            icon.Rescale(80, 80)

            if friend['online'] == '0':

                icon2 = icon.ConvertToBitmap()
                fdicon_sb = wx.StaticBitmap(friendpanel, id=index, bitmap=icon2, style=wx.BORDER_RAISED)
                fdicon_sb.Enable(False)
                fdname_st.Enable(False)
                fdqq_st.Enable(False)
                self.friendctrols.append((fdname_st, fdqq_st, fdicon_sb, icon2))

            else:
                icon2 = icon.ConvertToBitmap()
                #样式像浮雕隆起
                fdicon_sb = wx.StaticBitmap(friendpanel, id=index, bitmap=icon2, style=wx.BORDER_RAISED)
                fdicon_sb.Enable(True)
                fdname_st.Enable(True)
                fdqq_st.Enable(True)
                self.friendctrols.append((fdname_st, fdqq_st, fdicon_sb, icon2))


            #为好友图标、昵称、qq控件添加点击事件
            fdicon_sb.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
            fdname_st.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
            fdqq_st.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)

            #布局
            friendbox = wx.BoxSizer(wx.HORIZONTAL)
            friendbox.Add(fdicon_sb,1, wx.CENTER)
            friendbox.Add(fdname_st, 1, wx.CENTER)
            friendbox.Add(fdqq_st, 1, wx.CENTER)

            #单个好友控制面板
            friendpanel.SetSizer(friendbox)

            #添加好友到列表面板
            gridsizer.Add(friendpanel, 1, wx.ALL, border=5)

        panle.SetSizer(gridsizer)

        #场景整体box布局管理
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(toppanle, -1, wx.CENTER | wx.EXPAND)
        box.Add(panle, -1, wx.CENTER | wx.EXPAND)

        self.contentpanel.SetSizer(box)

        #初始化线程，设置子线程，接收客户端信息，刷新好友在线状态
        self.isrunning = True
        self.t1 = threading.Thread(target=self.thread_body)
        self.t1.start()


    def on_dclick(self, event): #打开聊天窗口
        #获得好友列表索引
        fid = event.GetId()

        #不能重复打开聊天窗口
        if self.chatFrame is not None and self.chatFrame.IsShown():
            dlg = wx.MessageDialog(self, '聊天窗口已打开',
                                    '操作失败',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        #停止当前窗口中的线程
        self.isrunning = False
        #使主线程阻塞
        self.t1.join()

        self.chatFrame = CharFrame(self, self.user, self.friends[fid])
        self.chatFrame.Show()

        #防止事件丢失
        event.Skip()

    #刷新好友列表
    def refreshfriendlist(self, onleuserlist):
        for index, friend in enumerate(self.friends):
            frienduserid = friend['user_id']
            fdname_st, fdqq_st, fdicon_sb, fdicon = self.friendctrols[index]
            if frienduserid in onleuserlist:
                fdicon_sb.Enable(True)
                fdname_st.Enable(True)
                fdqq_st.Enable(True)
                fdicon_sb.SetBitmap(fdicon)
            else:
                fdicon_sb.Enable(False)
                fdname_st.Enable(False)
                fdqq_st.Enable(False)
                fdicon_sb.SetBitmap(fdicon.ConvertToDisabled)

        #重绘窗口，显示更换之后的图片
        self.contentpanel.Layout()

    #线程体方法
    def thread_body(self):
        while self.isrunning:
            try:
                #从服务器接收数据
                json_data, _ = client_socket.recvfrom(1024)
                #json解码
                json_obj = json.loads(json_data.decode())
                print("json_obj", json_obj)
                logger.info("线程刷新好友从服务器接收数据：'{0}'".format(json_obj))
                cmd = json_obj['command']
                print("从服务器接收数据*****************", cmd)

                if cmd is not None:
                    if cmd == COMMAND_REFRESH:
                        userid_list = json_obj['OnlineUserlist']
                        if len(userid_list) > 0:
                            #刷新好友列表
                            print("刷新好友列表")
                            self.refreshfriendlist(userid_list)

                    elif cmd == COMMAND_SENDMSG:
                        print("收到服务器发过来消息")
                        fduserid = json_obj["user_id"]
                        msg = json_obj["message"]
                        print(msg)




            except Exception:
                continue
            time.sleep(2)

    #重启子线程
    def resetthread(self):
        #子线程运行状态
        self.isrunning = True
        self.t1 = threading.Thread(target=self.thread_body)
        self.t1.start()

    def OnClose(self, event):
        if self.chatFrame is not None and self.chatFrame.IsShown():
            dlg = wx.MessageDialog(
                self,"请先关闭聊天窗口，再退出程序",
                "操作失败",
                wx.OK | wx.ICON_ERROR
            )

            dlg.ShowModal()
            dlg.Destroy()
            return

        #当前用户下线，给服务器发送下线消息
        json_obj = {}
        json_obj["command"] = COMMAND_LOGOUT
        json_obj["user_id"] = self.user["user_id"]
        #JSON编码
        json_str = json.dumps(json_obj)
        client_socket.sendto(json_str.encode(), server_address)
        #停止当前子线程
        self.isrunning = False
        self.t1.join()
        self.t1 = None
        #关闭窗口
        super().OnClose()



