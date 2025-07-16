from fastapi import APIRouter, Depends, Body
from sqlalchemy import table
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
        print(1,platform_name, platform_logo, admin_username, admin_password, login_google_client, login_google_secret)
        # 验证必填字段
        if not all([platform_name, admin_username, admin_password]):
            return ResponseUtils.error("平台名称、管理员账号和密码为必填项")

        # 批量更新配置 
        configs = [
            (sys_config_key.KEY_PLATFORM_NAME, platform_name, "平台名称"),
            (sys_config_key.KEY_PLATFORM_LOGO, platform_logo, "平台logo"),
            (sys_config_key.KEY_ADMIN_USERNAME, admin_username, "管理员账号"),
            (sys_config_key.KEY_ADMIN_PASSWORD, admin_password, "管理员密码"),
            (sys_config_key.KEY_LOGIN_GOOGLE_CLIENT, login_google_client, "谷歌登录客户端ID"),
            (sys_config_key.KEY_LOGIN_GOOGLE_SECRET, login_google_secret, "谷歌登录客户端密钥")
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
                }
            },
        })

    except Exception as e:
        return ResponseUtils.error(f"更新系统配置失败：{str(e)}")
    
