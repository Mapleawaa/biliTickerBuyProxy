from .server import ProxyServer

def main():
    server = ProxyServer()
    server.start()

if __name__ == '__main__':
    main()