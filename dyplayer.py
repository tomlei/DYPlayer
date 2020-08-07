from machine import UART


_DISK_USB   = 0x00
_DISK_SD    = 0x01
_DISK_FLASH = 0x02
_DISK_NO    = 0xFF

_PLAY_STATUS_STOP  = 0x00       # 播放状态:停止
_PLAY_STATUS_START = 0x01       # 播放状态:播放
_PLAY_STATUS_PAUSE = 0x02       # 播放状态:暂停

_PLAY_MODEL_ALL_LOOP    = 0x00  # 播放模式: 全盘循环
_PLAY_MODEL_SINGLE_LOOP = 0x01  # 播放模式: 单曲循环
_PLAY_MODEL_SINGLE_STOP = 0x02  # 播放模式: 单曲停止


class DYPlayer():
    """DY-SV17F模块驱动
        使用ESP8266上的UART1中TX端口发送控制指令
        使用Flash
    """
    def __init__(self):
        self._uart = UART(1, 9600)

    def set_play_model(self, play_model=_PLAY_MODEL_SINGLE_LOOP):
        """设置循环模式"""
        self._send_command(bytearray([0x18, 0x01, play_model]))

    def set_loop_num(self, loop_num=30):
        """设置循环次数
            指令:AA 19 02 次数高 次数低 SM
        """
        h_value = loop_num & 0b1111111100000000
        l_value = loop_num & 0b0000000011111111
        self._send_command(bytearray([0x19, 0x02, h_value, l_value]))
        
    def _get_sm(self, buff):
        """获取和检验
            为之前所有字节之和的低8位,即起始码到数据相加后取低8位。
        """
        value = 0
        
        for i in range(len(buff)):
            value += buff[i]
        
        return value & 0b0000000011111111

    def _send_command(self, cmd_buff):
        """发送指令给模块"""
        cmd_buff = bytearray([0xaa]) + cmd_buff
        sm       = self._get_sm(cmd_buff)
        self._uart.write(cmd_buff + bytearray([sm]))
        
    def set_volume(self, num):
        """音量设置"""
        self._send_command(bytearray([0x13, 0x01, num]))
        
    def play(self, single_name="/00001.mp3"):
        """播放指定盘符指定路径的文件"""
        single_name = single_name.replace(".", "*").upper()
        buff = bytearray(3 + len(single_name))
        buff[0] = 0x08
        buff[1] = len(single_name) + 1
        buff[2] = _DISK_FLASH

        for i in range(len(single_name)):
            buff[3 + i] = ord(single_name[i])
            
        self._send_command(buff)

    def stop(self):
        """停止"""
        self._send_command(bytearray([0x04, _PLAY_STATUS_STOP]))

