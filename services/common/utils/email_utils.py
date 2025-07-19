import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sqlalchemy.orm import Session
from services.admin_service.services.sys_config_service import SysConfigService
from services.admin_service.constants import sys_config_key
from services.common.config import Config


class EmailUtils:
    """
    邮件工具类 - 从系统配置中读取邮件设置
    优先使用系统配置，如果没有配置则回退到环境变量配置
    """

    @staticmethod
    def get_email_config(db: Session) -> dict:
        """
        从系统配置中获取邮件配置
        :param db: 数据库会话
        :return: 邮件配置字典
        """
        sysconfig_service = SysConfigService(db)
        
        smtp_host = sysconfig_service.get_value_by_key(sys_config_key.KEY_EMAIL_SMTP_HOST)
        smtp_port = sysconfig_service.get_value_by_key(sys_config_key.KEY_EMAIL_SMTP_PORT)
        smtp_user = sysconfig_service.get_value_by_key(sys_config_key.KEY_EMAIL_SMTP_USER)
        smtp_password = sysconfig_service.get_value_by_key(sys_config_key.KEY_EMAIL_SMTP_PASSWORD)
        smtp_sender = sysconfig_service.get_value_by_key(sys_config_key.KEY_EMAIL_SMTP_SENDER)
        
        # 如果系统配置中有SMTP配置，则使用系统配置
        if smtp_host and smtp_port and smtp_user and smtp_password:
            return {
                'host': smtp_host,
                'port': int(smtp_port),
                'user': smtp_user,
                'password': smtp_password,
                'sender': smtp_sender or smtp_user,  # 如果没有指定发送者，使用用户名
            }
        
        # 否则回退到环境变量配置
        logging.warning("系统配置中未找到完整的邮件配置，使用环境变量配置")
        return {
            'host': Config.SMTP_HOST,
            'port': Config.SMTP_PORT,
            'user': Config.SMTP_USER,
            'password': Config.SMTP_PASSWORD,
            'sender': Config.SMTP_SENDER,
        }

    @staticmethod
    def send_email(
        db: Session,
        subject: str,
        body: str,
        to: str,
        is_html: bool = False,
    ) -> bool:
        """
        发送邮件，使用动态配置
        :param db: 数据库会话
        :param subject: 邮件主题
        :param body: 邮件正文
        :param to: 收件人邮箱
        :param is_html: 是否为HTML内容
        :return: 是否发送成功
        """
        try:
            # 获取邮件配置
            email_config = EmailUtils.get_email_config(db)
            
            sender = email_config['sender']
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = to
            msg["Subject"] = subject

            logging.info(f"使用动态配置发送邮件 SMTP host: {email_config['host']}")

            if is_html:
                msg.attach(MIMEText(body, "html", "utf-8"))
            else:
                msg.attach(MIMEText(body, "plain", "utf-8"))

            # 根据端口选择连接方式
            if email_config['port'] == 465:
                server = smtplib.SMTP_SSL(email_config['host'], email_config['port'])
            else:
                server = smtplib.SMTP(email_config['host'], email_config['port'])
                server.starttls()
            
            server.login(email_config['user'], email_config['password'])
            server.sendmail(sender, [to], msg.as_string())
            server.quit()
            
            logging.info(f"邮件发送成功到 {to}")
            return True
            
        except Exception as e:
            logging.error(f"发送邮件失败: {e}")
            return False

    @staticmethod
    def test_email_config(db: Session) -> tuple[bool, str]:
        """
        测试邮件配置是否有效
        :param db: 数据库会话
        :return: (是否成功, 错误信息)
        """
        try:
            email_config = EmailUtils.get_email_config(db)
            
            # 尝试连接SMTP服务器
            if email_config['port'] == 465:
                server = smtplib.SMTP_SSL(email_config['host'], email_config['port'])
            else:
                server = smtplib.SMTP(email_config['host'], email_config['port'])
                server.starttls()
            
            server.login(email_config['user'], email_config['password'])
            server.quit()
            
            return True, "邮件配置测试成功"
            
        except Exception as e:
            return False, f"邮件配置测试失败: {str(e)}"

    @staticmethod
    def send_register_code_email(db: Session, email: str, confirm_code: str) -> bool:
        """
        发送注册验证码邮件（使用HTML模板）
        
        Args:
            db: 数据库会话
            email: 收件人邮箱
            confirm_code: 验证码
            
        Returns:
            bool: 是否发送成功
        """
        try:
            from services.common.utils.email_template_utils import EmailTemplateUtils
            
            # 渲染邮件模板
            html_content = EmailTemplateUtils.render_register_code_email(db, confirm_code)
            if not html_content:
                logging.error("渲染邮件模板失败")
                return False
            
            # 获取平台配置用于邮件主题
            platform_config = EmailTemplateUtils.get_platform_config(db)
            subject = f"👋Your verification code for {platform_config['platform_name']}"
            
            # 发送HTML邮件
            return EmailUtils.send_email(db, subject, html_content, email, is_html=True)
            
        except Exception as e:
            logging.error(f"发送注册验证码邮件失败: {str(e)}")
            return False
