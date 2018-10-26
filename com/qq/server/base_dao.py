"""定义DAO基类---数据库连接"""
import pymysql
import configparser     #读取配置文件
import logging      #日志模块

logger = logging.getLogger(__name__)

class BaseDao(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        host = self.config['db']['host']
        user = self.config['db']['user']
        password = self.config['db']['password']
        database = self.config['db']['database']
        charset = self.config['db']['charset']

        port = self.config.getint('db','port')  #端口是整数,上面读出来是字符串

        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    port=port,
                                    password=password,
                                    database = database,
                                    charset=charset)

    def close(self):
        """关闭数据库连接"""
        self.conn.close()