from fastapi import APIRouter, Depends, Body
from sqlalchemy import false, table
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.sys_config_service import SysConfigService
from services.admin_service.constants import sys_config_key

router = APIRouter()




def get_sysconfig_service(db: Session = Depends(get_db)) -> SysConfigService:
    return SysConfigService(db)


@router.get("/")
def get_sysconfig(
    sysconfig_service: SysConfigService = Depends(get_sysconfig_service)
    ):
    platform_name = sysconfig_service.get_value_by_key(sys_config_key.KEY_PLATFORM_NAME)
    platform_logo = sysconfig_service.get_value_by_key(sys_config_key.KEY_PLATFORM_LOGO)
    admin_username = sysconfig_service.get_value_by_key(sys_config_key.KEY_ADMIN_USERNAME)
    login_google_client = sysconfig_service.get_value_by_key(sys_config_key.KEY_LOGIN_GOOGLE_CLIENT)
    login_google_secret = sysconfig_service.get_value_by_key(sys_config_key.KEY_LOGIN_GOOGLE_SECRET)
    login_google_enable = sysconfig_service.get_value_by_key(sys_config_key.KEY_LOGIN_GOOGLE_ENABLE)
    if not login_google_enable:
        login_google_enable = False
    else:
        login_google_enable = bool(login_google_enable)
    return ResponseUtils.success(data={
        "platform": {
            "name": platform_name,
            "logo": platform_logo,
        },
        "account":{
            "username": admin_username,
        },
        "login":{
            "google":{
                "client": login_google_client,
                "secret": login_google_secret,
                "is_enabled": login_google_enable,
            }
        },
    })

@router.put("/")
def set_sysconfig(
    sysconfig_service: SysConfigService = Depends(get_sysconfig_service),
    body: dict = Body(...),
    ):
    try:
        platform_name = body["platform"]["name"]
        platform_logo = body["platform"]["logo"]
        admin_username = body["account"]["username"]
        admin_password = body["account"]["password"]
        login_google_client = body["login"]["google"]["client_id"]
        login_google_secret = body["login"]["google"]["client_secret"]
        login_google_enable = body["login"]["google"]["is_enabled"]

        if not login_google_enable or login_google_enable == "false":
            login_google_enable = "False"
        else:
            login_google_enable = "True"
        # 批量更新配置 
        configs = [
            (sys_config_key.KEY_PLATFORM_NAME, platform_name, "平台名称"),
            (sys_config_key.KEY_PLATFORM_LOGO, platform_logo, "平台logo"),
            (sys_config_key.KEY_ADMIN_USERNAME, admin_username, "管理员账号"),
            (sys_config_key.KEY_ADMIN_PASSWORD, admin_password, "管理员密码"),
            (sys_config_key.KEY_LOGIN_GOOGLE_CLIENT, login_google_client, "谷歌登录客户端ID"),
            (sys_config_key.KEY_LOGIN_GOOGLE_SECRET, login_google_secret, "谷歌登录客户端密钥"),
            (sys_config_key.KEY_LOGIN_GOOGLE_ENABLE, login_google_enable, "谷歌登录是否启用"),
        ]

        for key, value, desc in configs:
            if value is not None:  # 只更新有值的配置
                sysconfig_service.set_value_by_key(key, value, desc)

        return ResponseUtils.success(data={
            "platform": {
                "name": platform_name,
                "logo": platform_logo,
            },
            "account":{
                "username": admin_username,
            },
            "login":{
                "google":{
                    "client": login_google_client,
                    "secret": login_google_secret,
                    "is_enabled": str_to_bool(login_google_enable),
                }
            },
        })

    except Exception as e:
        return ResponseUtils.error(f"更新系统配置失败：{str(e)}")
    
def str_to_bool(s):
    return s.lower() in ("true", "t", "yes", "y", "1")