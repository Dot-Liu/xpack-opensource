import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class HttpUtils:
    """HTTP请求工具类，提供通用的HTTP请求功能"""

    @staticmethod
    async def download_content_from_url(
        url: str,
        timeout: int = 30,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_content_types: Optional[list] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        从URL下载内容

        Args:
            url: 要下载的URL地址
            timeout: 请求超时时间（秒）
            max_file_size: 最大文件大小（字节）
            allowed_content_types: 允许的内容类型列表
            headers: 额外的请求头

        Returns:
            str: 下载的内容

        Raises:
            HTTPException: 当下载失败时
        """
        if allowed_content_types is None:
            allowed_content_types = [
                "application/json",
                "text/plain",
                "application/yaml",
                "text/yaml",
                "application/x-yaml",
                "text/x-yaml"
            ]

        try:
            logger.info(f"开始从URL下载内容: {url}")

            # 设置请求头
            request_headers = {
                "User-Agent": "XPack-OpenAPI-Downloader/1.0"
            }
            if headers:
                request_headers.update(headers)

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers=request_headers
            ) as session:
                async with session.get(url) as response:
                    # 检查响应状态
                    if response.status != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"无法下载内容，HTTP状态码: {response.status}"
                        )

                    # 检查内容类型
                    content_type = response.headers.get('content-type', '').lower()
                    if not any(ct in content_type for ct in allowed_content_types):
                        logger.warning(f"内容类型可能不正确: {content_type}")

                    # 检查文件大小
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > max_file_size:
                        raise HTTPException(
                            status_code=413,
                            detail=f"文件过大，最大允许 {max_file_size} 字节"
                        )

                    # 读取内容
                    content = await response.text()

                    # 检查实际内容大小
                    if len(content.encode('utf-8')) > max_file_size:
                        raise HTTPException(
                            status_code=413,
                            detail=f"文件过大，最大允许 {max_file_size} 字节"
                        )

                    logger.info(f"成功下载内容，大小: {len(content)} 字符")
                    return content

        except aiohttp.ClientError as e:
            logger.error(f"网络请求失败: {e}")
            raise HTTPException(status_code=400, detail=f"网络请求失败: {str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"请求超时: {url}")
            raise HTTPException(status_code=408, detail="请求超时")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"下载内容时发生错误: {e}")
            raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

    @staticmethod
    async def validate_url_accessibility(url: str, timeout: int = 10) -> bool:
        """
        验证URL是否可访问

        Args:
            url: 要验证的URL
            timeout: 超时时间（秒）

        Returns:
            bool: URL是否可访问
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.head(url) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"URL验证失败 {url}: {e}")
            return False

    @staticmethod
    async def get_url_info(url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        获取URL的基本信息

        Args:
            url: 要获取信息的URL
            timeout: 超时时间（秒）

        Returns:
            Dict[str, Any]: URL信息字典
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.head(url) as response:
                    return {
                        "status": response.status,
                        "content_type": response.headers.get('content-type', ''),
                        "content_length": response.headers.get('content-length'),
                        "last_modified": response.headers.get('last-modified'),
                        "server": response.headers.get('server', ''),
                        "accessible": response.status == 200
                    }
        except Exception as e:
            logger.debug(f"获取URL信息失败 {url}: {e}")
            return {
                "status": None,
                "content_type": "",
                "content_length": None,
                "last_modified": None,
                "server": "",
                "accessible": False,
                "error": str(e)
            }

    @staticmethod
    async def post_json(
        url: str,
        data: Dict[str, Any],
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发送JSON POST请求

        Args:
            url: 请求URL
            data: 要发送的数据
            timeout: 超时时间（秒）
            headers: 额外的请求头

        Returns:
            Dict[str, Any]: 响应数据

        Raises:
            HTTPException: 当请求失败时
        """
        try:
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "XPack-HTTP-Client/1.0"
            }
            if headers:
                request_headers.update(headers)

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers=request_headers
            ) as session:
                async with session.post(url, json=data) as response:
                    if response.status >= 400:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"HTTP请求失败，状态码: {response.status}"
                        )

                    return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"POST请求失败: {e}")
            raise HTTPException(status_code=400, detail=f"请求失败: {str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"POST请求超时: {url}")
            raise HTTPException(status_code=408, detail="请求超时")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"POST请求时发生错误: {e}")
            raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")
