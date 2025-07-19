"""
连接管理工具 - 帮助MCP客户端管理连接状态和重连
"""
import time
from typing import Dict, Optional
from dataclasses import dataclass
from services.api_service.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionInfo:
    """连接信息"""
    service_id: str
    user_id: str
    client_ip: str
    connected_at: float
    last_activity: float
    connection_count: int = 1


class ConnectionManager:
    """
    MCP连接管理器
    
    用于跟踪活跃连接，帮助诊断连接问题和支持重连逻辑
    """
    
    def __init__(self):
        self.connections: Dict[str, ConnectionInfo] = {}
        
    def register_connection(self, service_id: str, user_id: str, client_ip: str) -> str:
        """
        注册新连接
        
        Args:
            service_id: 服务ID
            user_id: 用户ID  
            client_ip: 客户端IP
            
        Returns:
            str: 连接标识符
        """
        connection_key = f"{service_id}:{user_id}:{client_ip}"
        current_time = time.time()
        
        if connection_key in self.connections:
            # 更新现有连接
            conn_info = self.connections[connection_key]
            conn_info.connected_at = current_time
            conn_info.last_activity = current_time
            conn_info.connection_count += 1
            logger.info(f"更新连接记录 - {connection_key}, 连接次数: {conn_info.connection_count}")
        else:
            # 创建新连接记录
            self.connections[connection_key] = ConnectionInfo(
                service_id=service_id,
                user_id=user_id,
                client_ip=client_ip,
                connected_at=current_time,
                last_activity=current_time
            )
            logger.info(f"注册新连接 - {connection_key}")
            
        return connection_key
        
    def update_activity(self, connection_key: str) -> None:
        """
        更新连接活动时间
        
        Args:
            connection_key: 连接标识符
        """
        if connection_key in self.connections:
            self.connections[connection_key].last_activity = time.time()
            
    def unregister_connection(self, connection_key: str) -> None:
        """
        注销连接
        
        Args:
            connection_key: 连接标识符
        """
        if connection_key in self.connections:
            conn_info = self.connections.pop(connection_key)
            duration = time.time() - conn_info.connected_at
            logger.info(f"注销连接 - {connection_key}, 持续时间: {duration:.2f}秒")
            
    def get_connection_info(self, connection_key: str) -> Optional[ConnectionInfo]:
        """
        获取连接信息
        
        Args:
            connection_key: 连接标识符
            
        Returns:
            Optional[ConnectionInfo]: 连接信息
        """
        return self.connections.get(connection_key)
        
    def get_service_connections(self, service_id: str) -> Dict[str, ConnectionInfo]:
        """
        获取指定服务的所有连接
        
        Args:
            service_id: 服务ID
            
        Returns:
            Dict[str, ConnectionInfo]: 连接信息字典
        """
        return {
            key: info for key, info in self.connections.items() 
            if info.service_id == service_id
        }
        
    def cleanup_stale_connections(self, timeout_seconds: int = 300) -> None:
        """
        清理超时的连接记录
        
        Args:
            timeout_seconds: 超时时间（秒）
        """
        current_time = time.time()
        stale_keys = [
            key for key, info in self.connections.items()
            if current_time - info.last_activity > timeout_seconds
        ]
        
        for key in stale_keys:
            logger.info(f"清理超时连接 - {key}")
            self.connections.pop(key, None)
            
    def get_stats(self) -> Dict:
        """
        获取连接统计信息
        
        Returns:
            Dict: 统计信息
        """
        total_connections = len(self.connections)
        services = set(info.service_id for info in self.connections.values())
        users = set(info.user_id for info in self.connections.values())
        
        return {
            "total_connections": total_connections,
            "unique_services": len(services),
            "unique_users": len(users),
            "services": list(services),
            "connection_details": [
                {
                    "key": key,
                    "service_id": info.service_id,
                    "user_id": info.user_id,
                    "client_ip": info.client_ip,
                    "connected_at": info.connected_at,
                    "last_activity": info.last_activity,
                    "duration": time.time() - info.connected_at,
                    "connection_count": info.connection_count
                }
                for key, info in self.connections.items()
            ]
        }


# 全局连接管理器实例
connection_manager = ConnectionManager()
