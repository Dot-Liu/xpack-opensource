# 从sys_config表读取配置，key配置在services/admin_service/constants/sys_config_key.py

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.sys_config_service import SysConfigService
from services.admin_service.constants.sys_config_key import (
    KEY_PLATFORM_NAME,
    KEY_PLATFORM_LOGO,
    KEY_WEBSITE_TITLE,
    KEY_HEADLINE,
    KEY_SUBHEADLINE,
    KEY_LOGIN_GOOGLE_CLIENT,
    KEY_LOGIN_GOOGLE_ENABLE,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config", summary="获取配置信息（无需登录）", tags=["common"])
def get_config(db: Session = Depends(get_db)):
    """获取公共配置信息，无需登录即可访问"""
    try:
        # 创建服务实例
        sys_config_service = SysConfigService(db)

        # 获取平台配置
        platform_name = sys_config_service.get_value_by_key(KEY_PLATFORM_NAME) or "XPack"
        platform_logo = sys_config_service.get_value_by_key(KEY_PLATFORM_LOGO) or ""
        website_title = sys_config_service.get_value_by_key(KEY_WEBSITE_TITLE) or ""
        headline = sys_config_service.get_value_by_key(KEY_HEADLINE) or ""
        subheadline = sys_config_service.get_value_by_key(KEY_SUBHEADLINE) or ""

        # 获取登录配置
        google_client_id = sys_config_service.get_value_by_key(KEY_LOGIN_GOOGLE_CLIENT) or ""
        google_is_enabled = sys_config_service.get_value_by_key(KEY_LOGIN_GOOGLE_ENABLE) or "false"

        # 构建响应数据
        config_data = {
            "login": {"google": {"client_id": google_client_id, "is_enabled": google_is_enabled}},
            "platform": {
                "name": platform_name, 
                "logo": platform_logo,
                "website_title": website_title,
                "headline": headline,
                "subheadline": subheadline,
            },
        }

        return ResponseUtils.success(data=config_data)
    except Exception as e:
        logger.error(f"Failed to get config: {str(e)}")
        return ResponseUtils.error(message="Failed to get configuration")
