import os
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from services.admin_service.services.sys_config_service import SysConfigService
from services.admin_service.constants import sys_config_key


class EmailTemplateUtils:
    """
    邮件模板工具类 - 处理邮件模板的加载和变量替换
    """

    @staticmethod
    def load_template(template_name: str) -> Optional[str]:
        """
        加载邮件模板文件
        
        Args:
            template_name: 模板文件名（不含路径和扩展名）
            
        Returns:
            Optional[str]: 模板内容，失败返回None
        """
        template_path = None
        try:
            # 构建模板文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(
                current_dir, 
                "..", 
                "..",  # 回到services目录
                "common",
                "templates", 
                "email", 
                f"{template_name}.html"
            )
            
            # 读取模板文件
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        except FileNotFoundError:
            logging.error(f"邮件模板文件不存在: {template_path}")
            return None
        except Exception as e:
            logging.error(f"读取邮件模板失败: {str(e)}")
            return None

    @staticmethod
    def get_platform_config(db: Session) -> Dict[str, str]:
        """
        从系统配置中获取平台信息
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, str]: 平台配置信息
        """
        try:
            sysconfig_service = SysConfigService(db)
            
            platform_name = sysconfig_service.get_value_by_key(sys_config_key.KEY_PLATFORM_NAME)
            platform_logo = sysconfig_service.get_value_by_key(sys_config_key.KEY_PLATFORM_LOGO)
            platform_url = sysconfig_service.get_value_by_key(sys_config_key.KEY_PLATFORM_URL)
            
            return {
                'platform_name': platform_name or 'XPack',
                'platform_logo_url': platform_logo or 'https://via.placeholder.com/100x20?text=XPack',
                'platform_url': platform_url or '#'
            }
            
        except Exception as e:
            logging.error(f"获取平台配置失败: {str(e)}")
            return {
                'platform_name': 'XPack',
                'platform_logo_url': 'https://via.placeholder.com/100x20?text=XPack',
                'platform_url': '#'
            }

    @staticmethod
    def render_template(template_content: str, variables: Dict[str, str]) -> str:
        """
        渲染邮件模板，替换变量
        
        Args:
            template_content: 模板内容
            variables: 要替换的变量字典
            
        Returns:
            str: 渲染后的HTML内容
        """
        try:
            rendered_content = template_content
            
            # 替换所有变量
            for key, value in variables.items():
                # 使用双花括号格式进行替换
                placeholder = f"{{{{{key}}}}}"
                rendered_content = rendered_content.replace(placeholder, str(value))
                
            return rendered_content
            
        except Exception as e:
            logging.error(f"渲染邮件模板失败: {str(e)}")
            return template_content

    @staticmethod
    def render_register_code_email(db: Session, confirm_code: str) -> Optional[str]:
        """
        渲染注册验证码邮件模板
        
        Args:
            db: 数据库会话
            confirm_code: 验证码
            
        Returns:
            Optional[str]: 渲染后的HTML内容，失败返回None
        """
        try:
            # 加载模板
            template_content = EmailTemplateUtils.load_template('email_register_code')
            if not template_content:
                return None
            
            # 获取平台配置
            platform_config = EmailTemplateUtils.get_platform_config(db)
            
            # 准备变量
            variables = {
                'platform_name': platform_config['platform_name'],
                'platform_logo_url': platform_config['platform_logo_url'],
                'confirm_code': confirm_code
            }
            
            # 渲染模板
            return EmailTemplateUtils.render_template(template_content, variables)
            
        except Exception as e:
            logging.error(f"渲染注册验证码邮件模板失败: {str(e)}")
            return None
