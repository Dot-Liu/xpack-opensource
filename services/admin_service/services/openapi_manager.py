import json
import logging
import yaml
from fastapi import UploadFile, HTTPException
from .openapi_helper import OpenApiForAI, convert_openapi_for_ai
from services.common.utils.http_utils import HttpUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenApiManager:
    """MCP管理器，负责处理OpenAPI文档的下载和解析"""

    def __init__(self, timeout: int = 30, max_file_size: int = 10 * 1024 * 1024):  # 10MB
        self.timeout = timeout
        self.max_file_size = max_file_size

    async def download_openapi_from_url(self, url: str) -> OpenApiForAI:
        """
        通过URL下载OpenAPI文档并解析为OpenApiForAI对象

        Args:
            url: OpenAPI文档的URL地址

        Returns:
            OpenApiForAI: 解析后的OpenAPI对象

        Raises:
            HTTPException: 当下载或解析失败时
        """
        try:
            logger.info(f"开始从URL下载OpenAPI文档: {url}")

            # 使用HttpUtils下载内容
            content = await HttpUtils.download_content_from_url(
                url=url,
                timeout=self.timeout,
                max_file_size=self.max_file_size,
                allowed_content_types=[
                    "application/json",
                    "text/plain",
                    "application/yaml",
                    "text/yaml",
                    "application/x-yaml",
                    "text/x-yaml",
                ],
            )

            logger.info(f"成功下载文档，大小: {len(content)} 字符")

            # 解析为OpenApiForAI对象
            return self._parse_openapi_content(content, f"URL: {url}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"下载OpenAPI文档时发生错误: {e}")
            raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

    async def parse_openapi_from_upload(self, file: UploadFile) -> OpenApiForAI:
        """
        从上传的文件中解析OpenAPI文档并转换为OpenApiForAI对象

        Args:
            file: 上传的文件对象

        Returns:
            OpenApiForAI: 解析后的OpenAPI对象

        Raises:
            HTTPException: 当文件无效或解析失败时
        """
        try:
            logger.info(f"开始处理上传文件: {file.filename}")

            # 检查文件名
            if not file.filename:
                raise HTTPException(status_code=400, detail="文件名不能为空")

            # 检查文件扩展名
            allowed_extensions = {".json", ".yaml", ".yml", ".txt"}
            file_extension = None
            if "." in file.filename:
                file_extension = "." + file.filename.rsplit(".", 1)[1].lower()

            if file_extension not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}")

            # 检查文件大小
            content = await file.read()
            if len(content) > self.max_file_size:
                raise HTTPException(status_code=413, detail=f"文件过大，最大允许 {self.max_file_size} 字节")

            if len(content) == 0:
                raise HTTPException(status_code=400, detail="文件内容为空")

            # 尝试解码文件内容
            try:
                content_str = content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    content_str = content.decode("gbk")
                except UnicodeDecodeError:
                    raise HTTPException(status_code=400, detail="文件编码不支持，请使用UTF-8或GBK编码")

            logger.info(f"成功读取文件内容，大小: {len(content_str)} 字符")

            # 解析为OpenApiForAI对象
            return self._parse_openapi_content(content_str, f"文件: {file.filename}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"处理上传文件时发生错误: {e}")
            raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

    def _parse_openapi_content(self, content: str, source: str) -> OpenApiForAI:
        """
        解析OpenAPI文档内容为OpenApiForAI对象

        Args:
            content: 文档内容字符串
            source: 内容来源描述（用于日志）

        Returns:
            OpenApiForAI: 解析后的OpenAPI对象

        Raises:
            HTTPException: 当解析失败时
        """
        try:
            # 先尝试作为JSON解析
            try:
                json.loads(content)
                logger.info(f"检测到JSON格式的OpenAPI文档 - {source}")
            except json.JSONDecodeError:
                # 如果不是JSON，尝试作为YAML处理
                try:
                    yaml_data = yaml.safe_load(content)
                    content = json.dumps(yaml_data, ensure_ascii=False)
                    logger.info(f"检测到YAML格式的OpenAPI文档，已转换为JSON - {source}")
                except ImportError:
                    raise HTTPException(status_code=500, detail="缺少YAML解析依赖，请安装PyYAML库或提供JSON格式文档")
                except yaml.YAMLError as e:
                    raise HTTPException(status_code=400, detail=f"YAML格式错误: {str(e)}")

            # 使用openapi_helper转换为OpenApiForAI对象
            openapi_for_ai = convert_openapi_for_ai(content)

            logger.info(f"成功解析OpenAPI文档 - {source}，包含 {len(openapi_for_ai.apis)} 个API端点")

            return openapi_for_ai

        except ValueError as e:
            logger.error(f"OpenAPI文档格式错误 - {source}: {e}")
            raise HTTPException(status_code=400, detail=f"OpenAPI文档格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"解析OpenAPI文档时发生未知错误 - {source}: {e}")
            raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")

    async def validate_openapi_url(self, url: str) -> bool:
        """
        验证URL是否有效且可访问

        Args:
            url: 要验证的URL

        Returns:
            bool: URL是否有效
        """
        return await HttpUtils.validate_url_accessibility(url, timeout=10)


# 创建全局实例
openapi_manager = OpenApiManager()
