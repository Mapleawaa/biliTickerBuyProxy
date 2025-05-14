import logging
import json
import os

# 尝试导入colorama，如果失败则使用空字符串作为替代
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    class DummyColors:
        def __getattr__(self, name):
            return ''
    Fore = Style = DummyColors()

# 配置logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "allowed_networks": ["172.16.1.", "192.168.1."],  # 允许多个网段
    "port_range": {
        "start": 7860,
        "end": 7961
    },
    "buffer_size": 4096
}

def load_config():
    """加载配置文件，如果不存在则创建默认配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if not os.path.exists(config_path):
        # 创建默认配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        logger.info(f'{Fore.YELLOW}已创建默认配置文件: {config_path}{Style.RESET_ALL}')
        return DEFAULT_CONFIG
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f'{Fore.GREEN}成功加载配置文件{Style.RESET_ALL}')
            return config
    except Exception as e:
        logger.error(f'{Fore.RED}加载配置文件失败，使用默认配置: {str(e)}{Style.RESET_ALL}')
        return DEFAULT_CONFIG

# 加载配置
config = load_config()

# 从配置文件获取配置项
ALLOWED_NETWORKS = config['allowed_networks']
GRADIO_PORT_RANGE = (config['port_range']['start'], config['port_range']['end'])
BUFFER_SIZE = config['buffer_size']