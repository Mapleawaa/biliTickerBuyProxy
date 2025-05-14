import socket
import threading
from .config import logger, Fore, Style, BUFFER_SIZE

class Connection:
    def __init__(self, client_socket, client_address, target_port, proxy_server):
        self.client_socket = client_socket
        self.client_address = client_address
        self.target_port = target_port
        self.proxy_server = proxy_server
        self.gradio_socket = None

    def start(self):
        """启动连接处理"""
        try:
            self.gradio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.gradio_socket.connect(('127.0.0.1', self.target_port))
            
            # 创建转发线程
            t1 = threading.Thread(target=self._forward, args=(self.client_socket, self.gradio_socket, "->"))
            t2 = threading.Thread(target=self._forward, args=(self.gradio_socket, self.client_socket, "<-"))
            
            t1.daemon = True
            t2.daemon = True
            
            self.proxy_server.add_connection(self)
            
            t1.start()
            t2.start()
            
        except Exception as e:
            logger.error(f'{Fore.RED}[端口 {self.target_port}] 处理连接时出错: {str(e)}{Style.RESET_ALL}')
            self.close()

    def _forward(self, src, dst, direction):
        """数据转发"""
        try:
            while self.proxy_server.is_running():
                try:
                    data = src.recv(BUFFER_SIZE)
                    if not data:
                        break
                    dst.send(data)
                    if direction == "->":
                        logger.debug(f'{Fore.BLUE}[端口 {self.target_port}] {self.client_address} -> Gradio{Style.RESET_ALL}')
                    else:
                        logger.debug(f'{Fore.GREEN}[端口 {self.target_port}] Gradio -> {self.client_address}{Style.RESET_ALL}')
                except socket.error:
                    break
        finally:
            self.close()

    def close(self):
        """关闭连接"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        if self.gradio_socket:
            try:
                self.gradio_socket.close()
            except:
                pass
        self.proxy_server.remove_connection(self)