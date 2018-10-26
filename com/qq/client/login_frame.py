
"""用户登录窗口"""
import json
from com.qq.client.friends_frame import FriendsFrame
from com.qq.client.my_frame import *

class LoginFrame(MyFrame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, u'QQ2006', size=(400, 300), pos=(1500, 100))

        mypanel = wx.Panel(self, -1, size=(400, 300))

        # 声明图片对象

        image = wx.Image('resources/images/88.jpg', wx.BITMAP_TYPE_JPEG)

        # print('图片的尺寸为{0}x{1}'.format(image.GetWidth(), image.GetHeight()))
        image.Rescale(400, 50)

        mypic = image.ConvertToBitmap()
        # 显示图片

        wx.StaticBitmap(mypanel, -1, bitmap=mypic, pos=(2, 2))

        middlepanel = wx.Panel(parent=self, style=wx.BORDER_DOUBLE, pos=(0, 50), size=(400, 250))

        accountid_st = wx.StaticText(middlepanel, wx.ID_ANY, 'QQ号码', pos=(50, 55))
        password_st = wx.StaticText(middlepanel, wx.ID_ANY, 'QQ密码', pos=(50, 105))

        self.accountid_txt = wx.TextCtrl(middlepanel, pos=(130, 50))
        self.password_txt = wx.TextCtrl(middlepanel, style=wx.TE_PASSWORD, pos=(130, 100))

        okb_btn = wx.Button(middlepanel, -1, "登录", pos=(50, 160))
        self.Bind(wx.EVT_BUTTON, self.okb_btn_onclick, okb_btn)

        cancle_btn = wx.Button(middlepanel, -1, "取消", pos=(150, 160))
        self.Bind(wx.EVT_BUTTON, self.cancle_btn_onclick, cancle_btn)

        st = wx.StaticText(middlepanel, -1, '忘记密码?', pos=(260,110))
        st.SetForegroundColour(wx.BLUE)

        zc = wx.StaticText(middlepanel, -1, '注册帐号', pos=(280, 160))
        zc.SetForegroundColour(wx.BLUE)

    def okb_btn_onclick(self, event):
        account = self.accountid_txt.GetValue()
        password = self.password_txt.GetValue()
        json_obj = self.login(account, password)

        if  json_obj["result"] == "1":
            logger.info('登录成功')
            #界面跳转
            next_frame = FriendsFrame(json_obj)
            next_frame.Show()
            self.Hide()

        elif json_obj["result"] == "-1":
            logger.info('登录失败')
            dlg = wx.MessageDialog(self, 'qq帐号或密码错误',
                                   '登录失败',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        elif json_obj["result"] == "-2":
            logger.info('登录失败')
            dlg = wx.MessageDialog(self, '该帐号已经登录',
                                   '请勿重复登录',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

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
        logger.info('登录成功从服务器端接收数据:{0}'.format(json_obj))
        print(json_obj)
        return json_obj



