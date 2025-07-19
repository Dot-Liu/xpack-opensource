from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.utils.email_utils import EmailUtils
import logging

router = APIRouter()


@router.post("/send_template_email")
def send_template_email(
    body: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    测试发送模板邮件
    :param body: 包含邮箱地址和验证码的请求体 {"email": "test@example.com", "code": "123456"}
    :param db: 数据库会话
    :return: 发送结果
    """
    try:
        email = body.get("email")
        code = body.get("code", "123456")  # 默认验证码
        
        if not email:
            return ResponseUtils.error("请提供邮箱地址")
        
        # 发送模板邮件
        success = EmailUtils.send_register_code_email(db, email, code)
        
        if success:
            return ResponseUtils.success(data={"message": "模板邮件发送成功，请检查收件箱"})
        else:
            return ResponseUtils.error("模板邮件发送失败")
            
    except Exception as e:
        logging.error(f"发送模板邮件失败: {str(e)}")
        return ResponseUtils.error(f"发送模板邮件失败：{str(e)}")
