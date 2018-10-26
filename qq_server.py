
import logging
import socket
import json
import traceback
import time

from com.qq.server.user_dao import UserDao

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s'
                    '-%(name)s - %(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#服务器
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8000


#操作命令代码
COMMAND_LOGIN = 1 #登录
COMMAND_LOGOUT = 2 #下线
COMMAND_SENDMSG = 3 #发送消息
COMMAND_REFRESH = 4 #刷新好友

#所有已经登录的用户
clientlist = []


#初始化socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

logger.info('服务器启动，监听自己的端口{0}……'.format(SERVER_PORT))


#缓冲区
buffer = []

#主循环 单线程：等待客户端请求-接收到请求-处理-返回数据给客户端
while True:
    time.sleep(1)
    try:
        #获取客户端请求数据
        data, client_address = server_socket.recvfrom(1024)
        print("data:{1}, client_address{0}".format(data, client_address))
        json_obj = json.loads(data.decode())

        #提取客户端传递过来的操作命令
        command = json_obj['command']
        if command == COMMAND_LOGIN:

            userid = json_obj['user_id']
            userpwd = json_obj['user_pwd']
            # if userid in map(lambda it: it[0], clientlist):
            #     json_obj = {}
            #     json_obj['result'] = '-2'
            #     # Json解码
            #     json_str = json.dumps(json_obj)
            #     server_socket.sendto(json_str.encode(), client_address)

            logger.debug('user_id:{0} user_pwd:{1}'.format(userid, userpwd))
            dao = UserDao()
            user = dao.findbyid(userid)
            logger.info(user)

            #判断客户端发送过来的密码与数据库中的密码是否一至
            if user is not None and user['user_pwd'] == userpwd:
                #登录成功
                logger.info('登录成功')
                #在线用户添加到列表
                clientinfo = (userid, client_address)
                clientlist.append(clientinfo)
                print("在线好友列表",clientlist)

                #给客户端准备数据
                json_obj = {}
                json_obj["user"] = user
                json_obj['result'] = '1'

                #取出好友列表
                dao = UserDao()
                friends = dao.findfriends(userid)
                #返回在线好友id
                cinfo_userids = map(lambda it: it[0], clientlist)

                for friend in friends:
                    fid = friend['user_id']
                    #添加好友状态，1在线0离线
                    friend['online'] = '0'
                    if fid in cinfo_userids:
                        friend['online'] = '1'

                json_obj['friends'] = friends
                logger.info('服务器给客户端发送用户登录成功,消息{0}'.format(json_obj))

                #json解码
                json_str = json.dumps(json_obj)
                #给客户端发送数据
                server_socket.sendto(json_str.encode(), client_address)

            else:
                json_obj = {}
                json_obj['result'] = '-1'
                #Json解码
                json_str = json.dumps(json_obj)
                server_socket.sendto(json_str.encode(), client_address)

        elif command == COMMAND_SENDMSG:
            print("服务器收到消息")
            receive_user_id = json_obj["receive_user_id"]
            user_id = json_obj["user_id"]
            message = json_obj["message"]

            filter_clinetinfo = filter(lambda it: it[0] == receive_user_id, clientlist)
            clientinfo = list(filter_clinetinfo)
            if len(clientinfo) == 1:
                _, client_address = clientinfo[0]
                print("该好友在线,消息转发给该好友")

                json_str = json.dumps(json_obj)
                server_socket.sendto(json_str.encode(), client_address)

        elif command == COMMAND_LOGOUT:
            userid = json_obj["user_id"]
            for client in clientlist:
                clientid, _ = client
                if clientid == userid:
                    clientlist.remove(client)
                    break



        #刷新好友列表 clientlist为空跳到下一次循环
        if len(clientlist) == 0:
            continue

        json_obj = {}
        json_obj["command"] = COMMAND_REFRESH
        #返回在线好友id
        userids_map = map(lambda it: it[0], clientlist)
        userid_list = list(userids_map)

        json_obj["OnlineUserlist"] = userid_list

        for clientinfo in clientlist:
            _, address = clientinfo
            #json解码
            json_str = json.dumps(json_obj)
            #给客户端发送数据
            server_socket.sendto(json_str.encode(), address)

    except Exception:
        traceback.print_exc()