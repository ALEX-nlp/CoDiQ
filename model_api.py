from openai import OpenAI
from loguru import logger
import itertools
from threading import Lock

class MultiPortOpenAIClient:
    def __init__(self, endpoints=None, servers=None, api_key=None):
        """
        初始化多端点客户端
        
        Args:
            endpoints: URL列表，如 ["https://api.deepseek.com", ...]
            servers: 服务器配置列表，如 [{"host": "127.0.0.1", "ports": [22020, 22021]}, ...]
            api_key: API密钥
        """
        self.clients = []
        
        # 方式1：直接使用endpoints列表
        if endpoints:
            for endpoint in endpoints:
                base_url = endpoint
                client = OpenAI(base_url=base_url, api_key=api_key)
                self.clients.append({
                    "client": client,
                    "endpoint": endpoint,
                    "base_url": base_url
                })
        
        # 方式2：使用servers配置生成endpoints
        elif servers:
            for server in servers:
                host = server["host"]
                ports = server["ports"]
                for port in ports:
                    endpoint = f"http://{host}:{port}"
                    base_url = f"{endpoint}/v1"
                    client = OpenAI(base_url=base_url, api_key=api_key)
                    self.clients.append({
                        "client": client,
                        "endpoint": endpoint,
                        "base_url": base_url,
                        "host": host,
                        "port": port
                    })
        
        if not self.clients:
            raise ValueError("必须提供 endpoints 或 servers 配置")
        
        # 使用itertools.cycle实现轮询
        self.client_cycle = itertools.cycle(self.clients)
        self.lock = Lock()
        
        logger.info(f"Initialized MultiPortOpenAIClient with {len(self.clients)} endpoints")
        for idx, client_info in enumerate(self.clients):
            logger.info(f"  [{idx}] {client_info['endpoint']}")
    
    def get_next_client(self):
        """获取下一个client（线程安全）"""
        with self.lock:
            client_info = next(self.client_cycle)
        # logger.debug(f"Using endpoint: {client_info['endpoint']}")
        return client_info["client"], client_info["endpoint"]