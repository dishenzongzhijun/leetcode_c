# import win32con
# import win32api
# import win32gui
from cmath import log
import ctypes
from ctypes import *
import winreg
import sys, os
import time
import threading
import logging
import subprocess
from threading import Thread

import serial
import serial.tools.list_ports

import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from debugsys import TaskReadUsb, TaskWriteUsb, TaskDealer, MBOX_Frame_Head, send_data_to_driver, set_comp_cb_func, r_queue, w_queue
from websocket import send_msg
# logging.info(sys.path)

# DBT_DEVNODES_CHANGED
# 0x0007	A device has been added to or removed from the system.
# DBT_QUERYCHANGECONFIG
# 0x0017	Permission is requested to change the current configuration (dock or undock).
# DBT_CONFIGCHANGED
# 0x0018	The current configuration has changed, due to a dock or undock.
# DBT_CONFIGCHANGECANCELED
# 0x0019	A request to change the current configuration (dock or undock) has been canceled.
# DBT_DEVICEARRIVAL
# 0x8000	A device or piece of media has been inserted and is now available.
# DBT_DEVICEQUERYREMOVE
# 0x8001	Permission is requested to remove a device or piece of media. Any application can deny this request and cancel the removal.
# DBT_DEVICEQUERYREMOVEFAILED
# 0x8002	A request to remove a device or piece of media has been canceled.
# DBT_DEVICEREMOVEPENDING
# 0x8003	A device or piece of media is about to be removed. Cannot be denied.
# DBT_DEVICEREMOVECOMPLETE
# 0x8004	A device or piece of media has been removed.
# DBT_DEVICETYPESPECIFIC
# 0x8005	A device-specific event has occurred.
# DBT_CUSTOMEVENT
# 0x8006	A custom event has occurred.
# DBT_USERDEFINED
# 0xFFFF	The meaning of this message is user-defined.

# LRESULT CALLBACK WindowProc(HWND   hwnd,     // handle to window
#                             UINT   uMsg,     // WM_DEVICECHANGE
#                             WPARAM wParam,   // device-change event
#                             LPARAM lParam ); // event-specific data


# Device change events (WM_DEVICECHANGE wparam)
DBT_DEVICEARRIVAL = 0x8000              # arrival
DBT_DEVICEQUERYREMOVE = 0x8001
DBT_DEVICEQUERYREMOVEFAILED = 0x8002
DBT_DEVICEMOVEPENDING = 0x8003
DBT_DEVICEREMOVECOMPLETE = 0x8004       # remove
DBT_DEVICETYPESSPECIFIC = 0x8005
DBT_CONFIGCHANGED = 0x0018

# type of device in DEV_BROADCAST_HDR
DBT_DEVTYP_OEM = 0x00000000              # OEM 或 IHV 定义的设备类型。这个结构是一个 DEV_BROADCAST_OEM结构。
DBT_DEVTYP_DEVNODE = 0x00000001
DBT_DEVTYP_VOLUME = 0x00000002           # 音量
DBT_DEVTYPE_PORT = 0x00000003            # 端口设备（串行或并行）。这个结构是一个 DEV_BROADCAST_PORT结构。
DBT_DEVTYPE_NET = 0x00000004
DBT_DEVTYP_DEVICEINTERFACE = 0x00000005  # 设备类别。这个结构是一个 DEV_BROADCAST_DEVICEINTERFACE结构。
DBT_DEVTYP_HANDLE = 0x00000006           # 文件系统句柄。这个结构是一个 DEV_BROADCAST_HANDLE结构。

WORD = ctypes.c_ushort
DWORD = ctypes.c_ulong
WCHAR = ctypes.c_wchar

STATE_DISCONNETED = 0
STATE_FASTBOOT = 1
STATE_CONNETED = 2

PORT_NAME_FINGERPRINT = "Fingerprint"
PORT_NAME_CDMA = "CDMA Modem"

serialcomm_sub_key = r"HARDWARE\DEVICEMAP\SERIALCOMM"
allserial_sub_key = r"SYSTEM\CurrentControlSet\Control\COM Name Arbiter\Devices"
# comm_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, serialcomm_sub_key, 0, winreg.KEY_READ)
# all_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, allserial_sub_key, 0, winreg.KEY_READ)

BOARD_TYPE_NONE = 0
BOARD_TYPE_UART = 1
BOARD_TYPE_USB = 2

Framework_ID = 0
MPROBE_PDT_INFO_LEN = 64
MPROBE_SN_LEN = 36
TIMESTAMP_LEN = 8
RESERVED_LEN = 10


class DEV_BROADCAST_PORT(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("dbcp_size", DWORD),
        ("dbcp_devicetype", DWORD),
        ("dbcp_reserved", DWORD),
        ("dbcp_name", WCHAR * 256),
    ]

class DEV_BROADCAST_HDR(ctypes.Structure):
    _fields_ = [
        ("dbch_size", DWORD),
        ("dbch_devicetype", DWORD),
        ("dbch_reserved", DWORD)
    ]


def get_board_state_name(state):
    if state == STATE_DISCONNETED:
        return "disconnected"
    elif state == STATE_FASTBOOT:
        return "fastboot"
    elif state == STATE_CONNETED:
        return "connected"
    else:
        return "unknown"

def get_board_type_name(type):
    if type == BOARD_TYPE_NONE:
        return "UNKNOW BOARD"
    elif type == BOARD_TYPE_UART:
        return "UART BOARD"
    elif type == BOARD_TYPE_USB:
        return "USB BOARD"
    else:
        return "ERROR BOARD"
    

def get_mprobe_state_name(mprobe_mgr):
    if not mprobe_mgr:
        return "no channel"
    if mprobe_mgr.state:
        return "connected"
    return "disconnected"

def websocket_send(msg):
    send_msg("boardmgr", msg)


def port_state_detect(state, board_id, port_list):
    boardmgr = get_boardmgr()
    if state == STATE_DISCONNETED:
        boardmgr.board_disconnect(board_id)
    elif state == STATE_CONNETED:
        boardmgr.board_connect(board_id, port_list)
    else:
        logging.error("no such state:{0}".format(state))


def get_serial_port_dic():
    port_dic = {}
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) == 0:
        logging.info("get no serial port")
    else:
        for i in range(0, len(port_list)):
            port_dic[port_list[i].device] = port_list[i].description
    # logging.info(port_dic)
    return port_dic

def check_current_board_by_serial():
    board_dic = {}
    try:
        all_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, serialcomm_sub_key, 0, winreg.KEY_READ)
    except WindowsError as e:
        logging.error("cannot find serialcomm_sub_key in windows")
        return board_dic

    port_dic = get_serial_port_dic()

    try:
        i = 0
        while 1:
            name, com, type = winreg.EnumValue(all_key, i)
            if com in port_dic:
                location = name.split("\\")[2]
                if 'AcmSerial' in location:
                    board_id = "AcmSerial"
                    if board_id not in board_dic:
                        board_dic[board_id] = [{"device": com, "description":port_dic[com]}]
                    else:
                        board_dic[board_id].append({"device": com, "description":port_dic[com]})
            i += 1
    except WindowsError as e:
        # logging.info(e)
        # logging.info(board_dic)
        # logging.info("enum done")
        pass

    finally:
        return board_dic

def check_current_board():
    board_dic = {}
    try:
        all_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, allserial_sub_key, 0, winreg.KEY_READ)
        # raise WindowsError
    except WindowsError as e:
        logging.error("cannot find serial keys in windows")
        board_dic = check_current_board_by_serial()
        return board_dic

    port_dic = get_serial_port_dic()

    try:
        i = 0
        while 1:
            name,value,type = winreg.EnumValue(all_key, i)
            if name in port_dic:
                location = value.split("#")[2]
                if '&' in location:
                    board_id = location.split("&")[1]
                    if board_id not in board_dic:
                        board_dic[board_id] = [{"device": name, "description":port_dic[name]}]
                    else:
                        board_dic[board_id].append({"device": name, "description":port_dic[name]})
            i += 1
    except WindowsError as e:
        # logging.info(e)
        # logging.info(board_dic)
        # logging.info("enum done")
        pass

    finally:
        return board_dic


current_boards = {}
def monitor():
    while True:
        global current_boards
        boards_new = check_current_board()
        add = set(boards_new).difference(current_boards)
        reduce = set(current_boards).difference(boards_new)
        if add:
            for board_id in add:
                logging.info("add board:{0}, port_list:{1}".format(board_id, boards_new[board_id]))
                port_state_detect(STATE_CONNETED, board_id, boards_new[board_id])
            current_boards = boards_new
            logging.info(current_boards)
        if reduce:
            for board_id in reduce:
                logging.info("reduce board:{0}, port_list:{1}".format(board_id, current_boards[board_id]))
                port_state_detect(STATE_DISCONNETED, board_id, current_boards[board_id])
            current_boards = boards_new
            logging.info(current_boards)

        time.sleep(3)


# def getFastbootSerial():
#     result_list = []
#     try:
#         logging.info("fastboot device")
#         p = subprocess.Popen('fastboot devices'.split(), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
#                                 stderr=subprocess.PIPE)
#         devices = p.communicate(timeout=10)[0]
#         serial_nos = []
#         for item in devices.split():
#             filters = ['fastboot']
#             item = str(item, encoding='utf-8')
#             if item.lower() not in filters:
#                 serial_nos.append(item)
#         logging.info("fastboot serial_nos")
#         logging.info(serial_nos)
#         result_list = serial_nos
#     except Exception as e:
#         print(e)
#     return result_list

def getFastbootSerial():
    result_list = []
    p = subprocess.Popen('fastboot devices'.split(), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    try:
        p.wait(10)
        devices = p.communicate()[0]
        serial_nos = []
        devices_str = devices.decode('gbk')
        for item in devices_str.splitlines():
            if item.lower().find("fastboot") >= 0:
                item_dst = item.split()
                if len(item_dst) == 2 and item_dst[1] == "fastboot":
                    serial_nos.append(item_dst[0])
        # logging.info("fastboot serial_nos")
        # logging.info(serial_nos)
        result_list = serial_nos
    except Exception as e:
        logging.info(e)
    return result_list

def check_fastboot_sn(sn, timeout=10):
    timer = time.time() + timeout
    while time.time() < timer:
        fastboot_sn = getFastbootSerial()
        if sn in fastboot_sn:
        # if fastboot_sn:
            logging.info("fastboot serial_nos")
            logging.info(fastboot_sn)
            return True
        time.sleep(1)
    logging.info("no fastboot serial_nos")
    return False


def gen_con_head():
    head = MBOX_Frame_Head()

    head.placeholder = 0x0
    head.service.sid = 0x8
    head.service.ver = 0x1
    head.service.midid = 0x2
    head.service.rsv = 0x0
    head.service.ssid = 0x1
    head.service.mt = 0x3
    head.service.frag_index = 0x2
    head.service.eof = 0x1
    head.service.ff = 0x0

    head.tran_src_c = 0x7d
    head.tran_port_c = 0x7e

    head.timestamp = 0x100f

    head.msg_id.msg_id = 0x0
    head.msg_id.comp_id = 0x0
    head.msg_id.rsv = 0x3

    head.msg_len.msg_len = len(gen_con_payload())
    head.msg_len.rsv = 0x6

    return head

def gen_con_payload():
    payload = ConSignal()

    payload.auid = 0x1
    payload.sn = 0x2
    payload.cmd = 0x3

    return payload.laod()

def gen_discon_head():
    head = MBOX_Frame_Head()

    head.placeholder = 0x0

    head.service.sid = 0x8
    head.service.ver = 0x1
    head.service.midid = 0x2
    head.service.rsv = 0x0
    head.service.ssid = 0x2
    head.service.mt = 0x3
    head.service.frag_index = 0x2
    head.service.eof = 0x1
    head.service.ff = 0x0

    head.tran_src_c = 0x7d
    head.tran_port_c = 0x7e

    head.timestamp = 0x100f

    head.msg_id.msg_id = 0x1
    head.msg_id.comp_id = 0x0
    head.msg_id.rsv = 0x3

    head.msg_len.msg_len = 0x5
    head.msg_len.rsv = 0x6
    # logging.info("size of head:{0}".format(sizeof(head)))

    return head

def gen_discon_payload():
    bytearr = bytearray()
    for i in range(5):
        bytearr.append(0x5)

    return bytes(bytearr)


class ConInfo(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
            ("auid", c_uint32),
            ("result", c_int32),
            ("authflag", c_uint16),
            ("authver", c_uint16),
            ("sn", c_char * MPROBE_SN_LEN),
            ("product_info", c_char * MPROBE_PDT_INFO_LEN),
            ("time_stamp", c_char * TIMESTAMP_LEN),
            ("aslr", c_ulong),
            # ("rsv", c_uint32 * RESERVED_LEN),
        ]

    def parse(self, byte):
        memmove(addressof(self), byte, sizeof(self))

class ConSignal(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
            ("auid", c_uint32),
            ("sn", c_uint32),
            ("cmd", c_uint32),
            # ("rsv", c_uint32),
        ]

    def laod(self):
        return string_at(addressof(self), sizeof(self))


def parse_con_payload(payload):
    msg = ConInfo()
    msg.parse(payload)
    logging.info(payload)
    logging.info("auid:{0}".format(msg.auid))
    logging.info("sn:{0}".format(str(msg.sn, encoding = "utf-8")))
    logging.info("result:{0}".format(msg.result))
    logging.info("authflag:{0}".format(msg.authflag))
    logging.info("authver:{0}".format(msg.authver))
    logging.info("product_info:{0}".format(str(msg.product_info, encoding = "utf-8")))
    logging.info("time_stamp:{0},{1}".format(type(msg.time_stamp), str(msg.time_stamp, encoding="utf-8", errors="ignore")))
    logging.info("aslr:{0}".format(msg.aslr))
    # logging.info("rsv:{0}".format(msg.rsv))
    return msg

def get_con_state(head, payload):
    boardmgr = get_boardmgr()
    board = boardmgr.current_board
    if not board:
        logging.error("cannot get current boards, please check")

    msg = parse_con_payload(payload)
    if msg.result != 0:
        logging.error("con info result:{0}".format(msg.result))
        return

    board.mprobe_mgr.state = True
    board.sn = str(msg.sn, encoding = "utf-8")
    board.product = str(msg.product_info, encoding = "utf-8")

    return msg

def check_proc_para(head, payload):
    if not payload:
        logging.error("payload null err")
        return False

    if not isinstance(head, MBOX_Frame_Head):
        logging.error("check_head_type err")
        return False

    if not isinstance(payload, bytes):
        logging.error("check_payload_type err")
        return False

    if head.msg_len.msg_len != len(payload):
        logging.error("msg_len err")
        return False

    return True

def framework_proc(head, payload):
    if not check_proc_para(head, payload):
        return

    msg_id = head.msg_id.msg_id
    logging.info("timestamp:{0}".format(head.timestamp))
    if msg_id == 0:
        logging.info("framework_proc 0")
        get_con_state(head, payload)
    elif msg_id == 1:
        logging.info("framework_proc 1")
    elif msg_id == 2:
        logging.info("framework_proc 2")
    else:
        logging.error("msg_id:{0} is not support".format(msg_id))


class Output(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self._transport = None
        logging.info("output init")

    def connection_made(self, transport):
        self._transport = transport
        logging.info('port opened:' + str(self._transport))
        self._transport.serial.rts = False
        # self._transport.write(b'Hello, World!\n')
        logging.info("enter send_conn_signal")
        conn_head = gen_con_head()
        conn_payload = gen_con_payload()
        logging.info(type(conn_payload))
        logging.info("start send_conn_signal")
        ret = send_data_to_driver(conn_head, conn_payload, self)
        if not ret[0]:
            logging.error(ret[1])
        else:
            logging.info(ret[1])

    def data_received(self, data):
        logging.info('data received')
        logging.info(str(data))
        # hdlc = HDLC(frame_callback=distrbute_frame_to_comp)
        # hdlc.decode(data)

    def connection_lost(self, exc):
        logging.info('port closed')
        self._transport.loop.stop()

    def pause_writing(self):
        logging.info('pause writing')
        logging.info(self._transport.get_write_buffer_size())

    def resume_writing(self):
        logging.info(self._transport.get_write_buffer_size())
        logging.info('resume writing')



def thread_loop_task(loop):
    logging.info("thread_loop_task")

    # 为子线程设置自己的事件循环
    # asyncio.set_event_loop(loop)

    from serial_asyncio import create_serial_connection
    coro = create_serial_connection(loop, Output, 'COM168', baudrate=115200)

    logging.info("thread_loop_task2")
    loop.run_until_complete(coro)


class MprobeManager:
    def __init__(self, serial):
        logging.info("MprobeManager init")
        # logging.info(serial)
        self.serial = serial
        self.state = False
        self.r_queue = r_queue
        self.w_queue = w_queue
        self.manager_init()

    def manager_init(self):
        self.open_channel()
        self.set_mprobe_mgr_cb()
        # self.send_conn_signal()

    def open_channel(self):

        self.r1 = TaskReadUsb(r_queue, self.serial)
        self.w1 = TaskWriteUsb(w_queue, self.serial)
        self.d1 = TaskDealer(self.r_queue)

        self.r1.start()
        self.d1.start()
        self.w1.start()

        # loop = asyncio.get_event_loop() 


        # 将thread_loop作为参数传递给子线程
        # t = threading.Thread(target=thread_loop_task, args=(loop,))
        # t.daemon = True
        # t.start()
        logging.info("open mprobe channel ok")

    def close_channel(self):
        self.r1.terminate()
        self.d1.terminate()
        self.w1.terminate()

        self.state = False

        logging.info("close mprobe channel ok")

    def send_conn_signal(self):
        logging.info("send_conn_signal")
        conn_head = gen_con_head()
        conn_payload = gen_con_payload()
        ret = send_data_to_driver(conn_head, conn_payload)
        if not ret[0]:
            logging.error(ret[1])
        else:
            logging.info(ret[1])

    def send_disconn_signal(self):
        conn_head = gen_discon_head()
        conn_payload = gen_discon_payload()
        ret = send_data_to_driver(conn_head, conn_payload)
        if not ret[0]:
            logging.error(ret[1])
        else:
            logging.info(ret[1])

    def set_mprobe_mgr_cb(self):
        set_comp_cb_func(Framework_ID, framework_proc)

    def check_con_state(self, timeout=5):
        timer = time.time() + timeout
        while time.time() < timer:
            if self.state:
                return True
            time.sleep(0.5)

        return False


class SerialPort:
    def __init__(self, com, name):
        self.com = com
        self.name = name
        self.state = STATE_DISCONNETED
        self.serial = None

    def open(self):
        try:
            self.serial = serial.Serial(self.com, baudrate=9600, bytesize=8,timeout=0.5)
            self.serial.reset_input_buffer()
            self.serial.set_buffer_size(rx_size=2147483647,tx_size=2147483647)
        except Exception as e:
            logging.info(e)
            self.state = STATE_DISCONNETED
            return None

        if self.serial.is_open:
            logging.critical(f"open {self.name}:{self.com} success")
            self.state = STATE_CONNETED
        else:
            logging.error("open failed")
            self.state = STATE_DISCONNETED

        return self.serial

    def close(self):
        if not self.serial:
            logging.error("this board have not Fingerprint/CDMA com or not open")
            return
        if self.serial.is_open:
            self.serial.close()
            logging.info("close success")
        else:
            logging.info("close already")
        self.state = STATE_DISCONNETED

    def read(self, size):
        all_bytes = self.serial.read(size=size)
        return all_bytes

    def write(self, data):
        number = self.serial.write(data)
        return number

    def check_port_state(self):
        return self.state


class Board:
    def __init__(self, id, port_list):
        self.id = id
        self.port_list = port_list
        self.ports = {}
        self.sn = ""
        self.product = ""
        self.mprobe_com = ""
        self.type = BOARD_TYPE_NONE
        self.state = STATE_CONNETED
        self.mprobe_mgr = None
        self.gen_port_init()

    def gen_port_init(self):
        for port in self.port_list:
            serialport = self.add_port(port["device"], port["description"])

            if PORT_NAME_FINGERPRINT in port["description"] or PORT_NAME_CDMA in port["description"]:
                self.mprobe_com = port["device"]
                ser = serialport.open()
                if not ser:
                    return
                # logging.info(ser)
                self.mprobe_mgr = MprobeManager(ser)

    def add_port(self, com, name):
        serialport = SerialPort(com, name)
        self.ports[com] = serialport
        return serialport

    def delete_port(self, com):
        if com in self.ports.keys():
            return self.ports.pop(com)
        else:
            logging.error("cannot delete board:{0}, not exist".format(com))

        return None

    def check_board_state(self):
        return self.state

    def check_mprobe_state(self):
        if not self.mprobe_mgr:
            # logging.info("not self.mprobe_mgr")
            return False
        # logging.info("not check_con_state")
        return self.mprobe_mgr.check_con_state()

    def check_mprobe_state_no_wait(self):
        if not self.mprobe_mgr:
            return False
        logging.info("check_mprobe_state_no_wait:{0}".format(self.mprobe_mgr.state))
        return self.mprobe_mgr.state


class UartBoard(Board):
    def __init__(self):
        pass

class UsbBoard(Board):
    def __init__(self):
        pass


from functools import wraps
def singleton(cls):
    instances = {}
    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return getinstance

@singleton
class BoardManager:
    def __init__(self):
        '''boards = {
            "board_id": board(object)
        } '''

        logging.critical("boardmgr init")
        self.boards = {}
        self.current_board = None
        self.gen_board_init()
        logging.critical("boardmgr init ok")

    def gen_board_init(self):
        board_dic = check_current_board()
        logging.info("init board:{0}".format(board_dic))
        global current_boards
        current_boards = board_dic
        for id, port_list in board_dic.items():
            self.add_board(id, port_list)
        self.show_boards()

    def manager_reset(self):
        self.boards = {}
        self.current_board = None
        # self.port_dic = get_serial_port_dic()
        self.gen_board_init()

    def add_board(self, id, port_list):
        if not port_list:
            logging.error("board:{0} have not port_list".format(id))
            return None

        port_dec_list = [port["description"] for port in port_list]
        board = None
        find_board = False
        for port_dec in port_dec_list:
            if "Interface" in port_dec:
                board = Board(id, port_list)
                board.type = BOARD_TYPE_USB
                self.boards[id] = board
                self.set_current_board(id)
                # logging.info("board:{0} is USB board, port_list:{1}".format(id, port_list))
                find_board = True
                break
                # board.open()
            elif "UART" in port_dec or "WCH" in port_dec:
                board = Board(id, port_list)
                board.type = BOARD_TYPE_UART
                self.boards[id] = board
                # logging.info("board:{0} is uart board, port_list:{1}".format(id, port_list))
                find_board = True
                break
        if not find_board:
            logging.info("board:{0} is unkown board, port_list:{1}".format(id, port_list))

        return board

    def delete_board(self, id):
        if id in self.boards.keys():
            if self.boards[id].mprobe_mgr:
                self.boards[id].mprobe_mgr.close_channel()
            # 检测当前单板是否被删除
            if self.boards[id] == self.current_board:
                self.current_board = None

            return self.boards.pop(id)
        else:
            logging.error("cannot delete board:{0}, not exist".format(id))

        return None

    def set_current_board(self, id):
        if id in self.boards.keys():
            self.current_board = self.boards[id]
            logging.critical("current board is:{0}".format(id))
        else:
            self.current_board = None
            logging.error("cannot find board:{0}".format(id))

        return self.current_board

    def get_current_board(self):
        return self.current_board

    def board_disconnect(self, board_id):
        logging.info("enter board_disconnect")
        find_boards_flag = False
        for id, board in self.boards.items():
            if board_id == id:
                find_boards_flag = True
                logging.info("find disconn board:{0}".format(id))
                if board.type == BOARD_TYPE_UART:
                    self.delete_board(id)
                    break
                if board.state == STATE_FASTBOOT:
                    break
                if check_fastboot_sn(board.sn):
                    board.state = STATE_FASTBOOT
                    for com, port in board.ports.items():
                        port.close()
                    if board.mprobe_mgr:
                        # board.mprobe_mgr.state = False
                        board.mprobe_mgr.close_channel()
                else:
                    # self.boards[id].state = STATE_DISCONNETED
                    self.delete_board(id)
                break

        if not find_boards_flag:
            logging.error("discon: not find board:{0}, please check".format(board_id))

        self.show_boards()

    def board_connect(self, board_id, port_list):
        logging.info("enter board_connect")
        find_boards_flag = False
        for id, board in self.boards.items():
            if board_id == id:
                find_boards_flag = True
                logging.info("find conn board:{0}".format(id))
                board.state = STATE_CONNETED
                break

        if not find_boards_flag:
            logging.info("from winreg find new board:{0}".format(board_id))
            self.add_board(board_id, port_list)

        self.show_boards()

    def open_port(self, id):
        if id in self.boards.keys():
            self.boards[id].open()
        else:
            logging.error("cannot open port which is belong to board:{0}, not exist".format(id))

    def close_port(self, id):
        if id in self.boards.keys():
            self.boards[id].close()
        else:
            logging.error("cannot close port which is belong to board:{0}, not exist".format(id))

    def open_uart_port(self, com):
        find_boards_flag = False
        for id, board in self.boards.items():
            for port in board.port_list:
                if com == port["device"]:
                    find_boards_flag = True
                    self.boards[id].ports[com].open()

        if not find_boards_flag:
            logging.error("cannot open uart port which is belong to board:{0}, not exist".format(com))

    def close_uart_port(self, com):
        find_boards_flag = False
        for id, board in self.boards.items():
            for port in board.port_list:
                if com == port["device"]:
                    find_boards_flag = True
                    self.boards[id].ports[com].close()
        if not find_boards_flag:
            logging.error("cannot close uart port which is belong to board:{0}, not exist".format(com))

    def get_boards(self):
        return self.boards

    def show_boards(self):
        logging.info("show_boards")
        logging.info("boards num: {0}".format(len(self.boards)))
        board_info = []
        for id, board in self.boards.items():
            logging.info("board:{0}--type:{1}--state:{2}".format(
                id, get_board_type_name(board.type), get_board_state_name(board.state)))
            # logging.info("board port_list:{0}".format(board.port_list))
            if board.type == BOARD_TYPE_USB:
                board_info.append({
                    "id": id,
                    "state": get_board_state_name(board.state),
                    "sn": board.sn,
                    "product": board.product,
                    "chan_state": get_mprobe_state_name(board.mprobe_mgr)
                })
        websocket_send(board_info)
        logging.info(board_info)





# boardmgr = BoardManager()
# p = threading.Thread(target=monitor)
# p.start()


def check_board_state(id=0):
    boardmgr = get_boardmgr()
    if id == 0:
        board = boardmgr.current_board
        if not board:
            return STATE_DISCONNETED
    else:
        if id not in boardmgr.boards.keys():
            return STATE_DISCONNETED

        board = boardmgr.boards[id]
    # fastboot or kernel
    return board.check_board_state()

def check_mprobe_state(id=0):
    ret = check_board_state(id)
    if ret != STATE_CONNETED:
        return False

    boardmgr = get_boardmgr()
    if id == 0:
        board = boardmgr.current_board
    else:
        board = boardmgr.boards[id]
    return board.check_mprobe_state()

def check_mprobe_state_no_wait(id=0):
    ret = check_board_state(id)
    if ret != STATE_CONNETED:
        return False

    boardmgr = get_boardmgr()
    if id == 0:
        board = boardmgr.current_board
    else:
        board = boardmgr.boards[id]
    return board.check_mprobe_state_no_wait()

def check_port_state(comm):
    boardmgr = get_boardmgr()
    for id, board in boardmgr.boards.items():
        for com, port in board.ports.items():
            if com == comm:
                return port.state
    logging.info("cannot find com:{0}".format(comm))
    return False


def mprobe_conncet(id=0):
    board_info = {"sn":"","product":""}
    ret = check_board_state(id)
    if ret == STATE_DISCONNETED:
        return (False, "board not connected")
    elif ret == STATE_FASTBOOT:
        return (False, "board in fastboot, please boot")

    boardmgr = get_boardmgr()
    if id == 0:
        board = boardmgr.current_board
    else:
        board = boardmgr.boards[id]
    if not board.mprobe_com:
        return (False, "this board not have Fingerprint/CDMA")

    # 已连接
    if check_mprobe_state_no_wait():
        board_info["id"] = board.id
        board_info["sn"] = board.sn
        board_info["product"] = board.product
        board_info["state"] = get_board_state_name(board.state)
        board_info["chan_state"] = get_mprobe_state_name(board.mprobe_mgr)
        return (True, board_info)

    if not board.ports[board.mprobe_com].check_port_state():
        board.mprobe_mgr.serial = board.ports[board.mprobe_com].open()
        board.mprobe_mgr.open_channel()
    
    board.mprobe_mgr.send_conn_signal()

    # ser = board.ports[board.mprobe_com].serial

    # logging.info(ser)
    # first conncet mprobe
    # if not board.mprobe_mgr:
    #     board.mprobe_mgr = MprobeManager(ser)
    # else:
    #     board.mprobe_mgr.serial = ser
    #     # board.mprobe_mgr.send_conn_signal()
    #     board.mprobe_mgr.manager_init()

    connect_ret = board.check_mprobe_state()
    logging.info("connect_ret:{0}".format(connect_ret))
    if not connect_ret:
        return (connect_ret, "connect auth fail, please check")

    board_info["id"] = board.id
    board_info["sn"] = board.sn
    board_info["product"] = board.product
    board_info["state"] = get_board_state_name(board.state)
    board_info["chan_state"] = get_mprobe_state_name(board.mprobe_mgr)
    return (connect_ret, board_info)

def auto_mprobe_conncet(id):
    check_ret = False
    while not check_ret:
        mprobe_conncet(id)
        check_ret = check_mprobe_state(id)

        time.sleep(10)


class BoardManagerHandler:
    def __init__(self):
        self.boardmgr = get_boardmgr()
        self.auto_check_mprobe = False

    def set_auto_check(self, id):
        auto_mprobe_conncet(id)

    def connect(self):
        mprobe_conncet(self.boardmgr.current_board)

def get_boardmgr() -> BoardManager:
    boardmgr = BoardManager()
    return boardmgr

def start_monitor():
    p = threading.Thread(target=monitor)
    p.start()