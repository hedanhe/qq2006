
"""用户登录窗口"""

import json

from com.qq.client.friends_frame import FriendsFrame
from com.qq.client.my_frame import *


class LoginFrame(MyFrame):

    def __init__(self):
        super().__init__(title="QQ登录", size=(400,300))

        #窗口顶部图片
        topimage = wx.Image('resources/images/88.jpg', wx.BITMAP_TYPE_JPEG)
        topimage.Rescale(400, 50)
        mypic = topimage.ConvertToBitmap()

        wx.StaticBitmap(self.contentpanel, bitmap=mypic, pos=(0,0))

        #创建中间面板和控件
        middlepanel = wx.Panel(self.contentpanel, style=wx.BORDER_DOUBLE)

        accountid_st = wx.StaticText(middlepanel, wx.ID_ANY, lable='QQ号码', pos=(50, 100))
        password_st = wx.StaticText(middlepanel, wx.ID_ANY, lable='QQ密码', pos=(50, 150))

        self.accountid_txt = wx.TextCtrl(middlepanel, pos=(250, 100))
        self.password_txt = wx.TextCtrl(middlepanel, style=wx.TE_PASSWORD, pos=(250, 150))

        st = wx.StaticText(middlepanel, wx.ID_ANY, '忘记密码?')
        st.SetForegroundColour(wx.BLUE)

        #创建FlexGrid布局
        fgs = wx.FlexGridSizer(3, 1, 8, 15)
        fgs.AddMany([
                        (accountid_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.FIXED_MINSIZE),
                     (self.accountid_txt, 1, wx.CENTER | wx.EXPAND),
                     wx.StaticText(middlepanel),

                     (password_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.FIXED_MINSIZE),
                     (self.accountid_txt, 1, wx.CENTER | wx.EXPAND),
                     (st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.FIXED_MINSIZE),

                     wx.StaticText(middlepanel),
                     (wx.CheckBox(middlepanel, -1, '自动登录'), 1, wx.CENTER | wx.EXPAND),
                     (wx.CheckBox(middlepanel, -1, '隐身登录'), 1, wx.CENTER | wx.EXPAND),

                     ])

        #设置FlexGrid布局

        fgs.AddGrowableRow(0, 1)
        fgs.AddGrowableRow(1, 1)

        fgs.AddGrowableCol(0, 1)
        fgs.AddGrowableCol(1, 1)
        fgs.AddGrowableCol(2, 1)

        paenlbox = wx.BoxSizer(wx.HORIZONTAL)
        paenlbox.Add(fgs, -1, wx.CENTER | wx.ALL | wx.EXPAND, border=10)
        middlepanel.SetSizer(paenlbox)

        #创建按钮对象
        okb_btn = wx.Button(parent=self.contentpanel, lable='登录')
        self.Bind(wx.EVT_BUTTON, self.okb_btn_onclick, okb_btn)

        cancle_btn = wx.Button(parent=self.contentpanel, lable='取消')
        self.Bind(wx.EVT_BUTTON, self.cancle_btn_onclick, cancle_btn)

        #创建水平Box布局
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.Button(parent=self.contentpanel, lable='申请号码↓'), 1, wx.CENTER | wx.ALL | wx.EXPAND, border=10)
        hbox.Add(okb_btn, 1, wx.CENTER | wx.ALL |wx.EXPAND, border=10)
        hbox.Add(cancle_btn, 1, wx.CENTER | wx.ALL | wx.EXPAND, border=10)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(topimage, -1, wx.CENTER | wx.ALL |wx.EXPAND, border=5)
        vbox.Add(middlepanel, -1, wx.CENTER | wx.ALL | wx.EXPAND)

        self.contentpanel.SetSizer(vbox)
    #
    #确定登录按钮
    def okb_btn_onclick(self, event):
        account = self.accountid_txt.GetValue()
        password = self.password_txt.GetValue()
        user = self.login(account, password)

        if user is not None:
            logger.info('登录成功')
            next_frame = FriendsFrame(user)
            next_frame.show()
            self.Hide()

        else:
            logger.info('登录失败')
            dlg = wx.MessageDialog(self, 'qq帐号或密码错误',
                                   '登录失败',
                                   wx.OK | wx.ICON_ERROR)
            dlg.showModal()
            dlg.Destroy()
    #取消按钮
    def cancle_btn_onclick(self, event):
        self.Destroy()
        sys.exit()


    def login(self, userid, password):
        """客户端向服务器发送请求"""

        json_obj = {}
        json_obj['command'] = COMMAND_LOGIN
        json_obj['user_id'] = userid
        json_obj['user_pwd'] = password

        #json编码
        json_str = json.dumps(json_obj)
        #给服务器发送数据
        client_socket.sendto(json_str.encode(), server_address)

        #等待服务器应答
        json_data, _ = client_socket.recvfrom(1024)
        #json解码
        json_obj = json.loads(json_data.decode())
        logger.info('从服务器端接收数据:{0}'.format(json_obj))

        if json_obj['result'] == '0':
            #登录成功
            return json_obj