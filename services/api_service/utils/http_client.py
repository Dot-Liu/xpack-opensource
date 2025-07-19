"""
HTTP客户端工具 - 负责构建和处理HTTP请求
"""
import json
from typing import Dict, Any, Optional
from services.common.logging_config import get_logger

logger = get_logger(__name__)


class HttpRequestBuilder:
    """HTTP请求构建器"""
    
    def build_request(self, tool_config, arguments: dict, auth_info: dict) -> Dict[str, Any]:
        """
        构建HTTP请求信息
        
        Args:
            tool_config: 工具配置
            arguments: 工具参数
            auth_info: 服务认证信息
            
        Returns:
            Dict[str, Any]: 请求信息字典
        """
        logger.debug(f"构建HTTP请求 - 工具: {tool_config.name}")
        logger.debug(f"原始路径: {tool_config.path}")
        logger.debug(f"HTTP方法: {tool_config.method.value}")
        logger.debug(f"传入参数: {arguments}")
        
        # 构建URL
        url = self._build_url(tool_config, arguments, auth_info)
        
        # 构建请求头
        headers = self._build_headers(tool_config, arguments, auth_info)
        
        # 构建查询参数
        query_params = self._build_query_params(tool_config, arguments)
        
        # 构建请求体
        request_body = self._build_request_body(tool_config, arguments)
        
        request_info = {
            "url": url,
            "method": tool_config.method.value,
            "headers": headers,
            "query_params": query_params,
            "request_body": request_body
        }
        
        logger.debug(f"构建完成的请求信息: {request_info}")
        return request_info
    
    def _build_url(self, tool_config, arguments: dict, auth_info: dict) -> str:
        """
        构建请求URL
        
        Args:
            tool_config: 工具配置
            arguments: 工具参数
            auth_info: 服务认证信息
            
        Returns:
            str: 完整的请求URL
        """
        base_url = auth_info.get("base_url", "")
        url = tool_config.path
        
        logger.debug(f"服务Base URL: {base_url}")
        
        # 如果工具路径不是完整URL，则拼接base_url
        if not url.startswith(("http://", "https://")) and base_url:
            base_url = base_url.rstrip("/")
            url = url.lstrip("/")
            url = f"{base_url}/{url}"
            logger.debug(f"URL拼接完成: {url}")
        else:
            logger.debug(f"使用原始URL: {url}")
        
        # 替换路径参数
        url = self._replace_path_parameters(url, tool_config, arguments)
        
        return url
    
    def _replace_path_parameters(self, url: str, tool_config, arguments: dict) -> str:
        """
        替换URL中的路径参数
        
        Args:
            url: 原始URL
            tool_config: 工具配置
            arguments: 工具参数
            
        Returns:
            str: 替换参数后的URL
        """
        if not tool_config.path_parameters:
            return url
        
        try:
            path_params = json.loads(tool_config.path_parameters)
            logger.debug(f"处理路径参数: {path_params}")
            
            for param in path_params:
                if isinstance(param, dict) and "name" in param:
                    param_name = param["name"]
                    if param_name in arguments:
                        url = url.replace(f"{{{param_name}}}", str(arguments[param_name]))
                        logger.debug(f"路径参数替换: {param_name} = {arguments[param_name]}")
            
            logger.debug(f"路径参数替换后URL: {url}")
            
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"路径参数解析失败: {e}")
        
        return url
    
    def _build_headers(self, tool_config, arguments: dict, auth_info: dict) -> Dict[str, str]:
        """
        构建请求头
        
        Args:
            tool_config: 工具配置
            arguments: 工具参数
            auth_info: 服务认证信息
            
        Returns:
            Dict[str, str]: 请求头字典
        """
        headers = {"User-Agent": "MCP Tool Server (XPack)"}
        
        # 添加认证头
        self._add_auth_headers(headers, auth_info)
        
        # 添加自定义请求头
        self._add_custom_headers(headers, tool_config, arguments)
        
        logger.debug(f"最终请求头: {headers}")
        return headers
    
    def _add_auth_headers(self, headers: Dict[str, str], auth_info: dict) -> None:
        """
        添加认证请求头
        
        Args:
            headers: 请求头字典
            auth_info: 认证信息
        """
        auth_method = auth_info.get("auth_method", "free")
        logger.debug(f"认证方法: {auth_method}")
        
        if auth_method != "free":
            auth_header = auth_info.get("auth_header")
            auth_token = auth_info.get("auth_token")
            if auth_header and auth_token:
                headers[auth_header] = auth_token
                # 隐藏token的详细信息，只显示前几位
                token_display = auth_token[:8] + "..." if len(auth_token) > 8 else "***"
                logger.debug(f"添加认证头: {auth_header} = {token_display}")
    
    def _add_custom_headers(self, headers: Dict[str, str], tool_config, arguments: dict) -> None:
        """
        添加自定义请求头
        
        Args:
            headers: 请求头字典
            tool_config: 工具配置
            arguments: 工具参数
        """
        if not tool_config.header_parameters:
            return
        
        try:
            header_params = json.loads(tool_config.header_parameters)
            logger.debug(f"处理自定义请求头: {header_params}")
            
            for param in header_params:
                if isinstance(param, dict) and "name" in param:
                    param_name = param["name"]
                    if param_name in arguments:
                        headers[param_name] = str(arguments[param_name])
                        logger.debug(f"添加自定义请求头: {param_name} = {arguments[param_name]}")
                        
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"请求头参数解析失败: {e}")
    
    def _build_query_params(self, tool_config, arguments: dict) -> Dict[str, Any]:
        """
        构建查询参数
        
        Args:
            tool_config: 工具配置
            arguments: 工具参数
            
        Returns:
            Dict[str, Any]: 查询参数字典
        """
        query_params = {}
        
        if not tool_config.query_parameters:
            return query_params
        
        try:
            query_param_defs = json.loads(tool_config.query_parameters)
            logger.debug(f"处理查询参数定义: {query_param_defs}")
            
            for param in query_param_defs:
                if isinstance(param, dict) and "name" in param:
                    param_name = param["name"]
                    if param_name in arguments:
                        query_params[param_name] = arguments[param_name]
            
            logger.debug(f"构建的查询参数: {query_params}")
            
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"查询参数解析失败: {e}")
        
        return query_params
    
    def _build_request_body(self, tool_config, arguments: dict) -> Optional[Dict[str, Any]]:
        """
        构建请求体
        
        Args:
            tool_config: 工具配置
            arguments: 工具参数
            
        Returns:
            Optional[Dict[str, Any]]: 请求体字典，如果不需要则返回None
        """
        if not tool_config.request_body_schema or tool_config.method.value not in ["POST", "PUT", "PATCH"]:
            return None
        
        try:
            body_schema = json.loads(tool_config.request_body_schema)
            logger.debug(f"请求体Schema: {body_schema}")
            
            if isinstance(body_schema, dict) and "properties" in body_schema:
                request_body = {}
                for prop_name in body_schema["properties"]:
                    if prop_name in arguments:
                        request_body[prop_name] = arguments[prop_name]
                
                logger.debug(f"构建的请求体: {request_body}")
                return request_body
                
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"请求体Schema解析失败: {e}")
        
        return None
