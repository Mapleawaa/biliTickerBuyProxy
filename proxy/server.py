import socket
import threading
import signal
import sys
from .config import logger, Fore, Style, GRADIO_PORT_RANGE, ALLOWED_NETWORKS
from .connection import Connection

class ProxyServer:
    def __init__(self):
        self._running = True
        self.target_ports = []
        self.connections = set()
        self.proxy_threads = []
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def find_gradio_ports(self):
        """扫描并找到所有Gradio服务端口"""
        found = False
        start_port, end_port = GRADIO_PORT_RANGE
        for port in range(start_port, end_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)  # 设置100ms的超时时间
                    result = s.connect_ex(('127.0.0.1', port))
                    if result == 0:
                        self.target_ports.append(port)
                        logger.info(f'{Fore.GREEN}找到Gradio服务端口: {port}{Style.RESET_ALL}')
                        found = True
            except socket.error:
                continue
        return found

    def start(self):
        """启动代理服务器"""
        if not self.find_gradio_ports():
            logger.error(f'{Fore.RED}未找到运行中的Gradio服务{Style.RESET_ALL}')
            return

        logger.info(f'{Fore.CYAN}允许来自 {ALLOWED_NETWORKS}0/24 网段的访问{Style.RESET_ALL}')
        logger.info(f'{Fore.CYAN}局域网用户可以通过 http://本机IP:端口号 访问对应服务{Style.RESET_ALL}')
        logger.info(f'{Fore.YELLOW}按 CTRL+C 可以安全停止所有服务{Style.RESET_ALL}')

        for port in self.target_ports:
            thread = threading.Thread(target=self._serve_port, args=(port,))
            thread.daemon = True
            self.proxy_threads.append(thread)
            thread.start()

        # 等待所有线程结束
        try:
            while self._running:
                for thread in self.proxy_threads[:]:
                    if not thread.is_alive():
                        self.proxy_threads.remove(thread)
                    thread.join(0.1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止代理服务器"""
        self._running = False
        self._close_all_connections()
        
        for thread in self.proxy_threads:
            thread.join(timeout=1.0)

    def is_running(self):
        """返回服务器运行状态"""
        return self._running

    def add_connection(self, connection):
        """添加新连接"""
        self.connections.add(connection)

    def remove_connection(self, connection):
        """移除连接"""
        self.connections.discard(connection)

    def _serve_port(self, port):
        """服务单个端口"""
        try:
            proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            proxy_socket.bind(('0.0.0.0', port))
            proxy_socket.listen(5)
            proxy_socket.settimeout(1)
            
            logger.info(f'{Fore.GREEN}[端口 {port}] 代理服务启动{Style.RESET_ALL}')
            
            while self._running:
                try:
                    client_socket, client_address = proxy_socket.accept()
                    # 检查是否来自允许的网段
                    if any(client_address[0].startswith(network) for network in ALLOWED_NETWORKS):
                        connection = Connection(client_socket, client_address, port, self)
                        connection.start()
                    else:
                        ALLOWED_NETWORKSs_str = '或'.join(ALLOWED_NETWORKS)
                        logger.warning(f'{Fore.RED}[端口 {port}] 拒绝来自 {client_address} 的连接 (仅允许 {ALLOWED_NETWORKSs_str} 网段访问){Style.RESET_ALL}')
                        client_socket.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        logger.error(f'{Fore.RED}[端口 {port}] socket错误: {str(e)}{Style.RESET_ALL}')
        finally:
            proxy_socket.close()

    def _close_all_connections(self):
        """关闭所有连接"""
        for conn in list(self.connections):
            conn.close()
        self.connections.clear()

    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        logger.info(f'{Fore.YELLOW}正在关闭所有代理服务...{Style.RESET_ALL}')
        self.stop()
        logger.info(f'{Fore.GREEN}所有代理服务已安全停止{Style.RESET_ALL}')
        sys.exit(0)