

import wx
import logging


from com.qq.client.login_frame import LoginFrame

#配置启动模块
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s'
                    '-%(name)s - %(funcName)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class App(wx.App):
    def OnInit(self):
        #创建登录窗口对象
        frame = LoginFrame()
        frame.Show()

        return True

if __name__ == '__main__':
    app = App()
    app.MainLoop()
