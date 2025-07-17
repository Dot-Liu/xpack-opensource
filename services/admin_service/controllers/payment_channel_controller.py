from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.payment_channel_service import PaymentChannelService

router = APIRouter()


def get_payment_channel(db: Session = Depends(get_db)) -> PaymentChannelService:
    return PaymentChannelService(db)

@router.get("/list")
async def payment_channel_list(
    page: int = Query(1, description="当前页码"),
    page_size: int = Query(15, description="当前页面数据条数"),
    payment_channel_service: PaymentChannelService = Depends(get_payment_channel),
):
    total, list = payment_channel_service.list()
    if total == 0:
        return ResponseUtils.success_page(data=[],total=0,page_num=page,page_size=page_size)
    result = []
    for item in list:
        enable = item.status == 1 
        result.append({
            "id": item.id,
            "name": item.name,
            "config": item.config,
            "is_enabled": enable,
            "updated_time": item.update_at,
        })
    return ResponseUtils.success_page(data=result,total=total,page_num=page,page_size=page_size)

@router.put("/enable")
async def payment_channel_enable(
    id: str,
    payment_channel_service: PaymentChannelService = Depends(get_payment_channel),
    ):
    data = payment_channel_service.update_status(id, 1)
    if data:
        return ResponseUtils.success({
            "id": id,
            "name": data.name,
            "config": data.config,
            "is_enabled": data.status == 1,
            "updated_time": data.update_at,
        })
    return ResponseUtils.success(data={})

@router.put("/disable")
async def payment_channel_disable(
    id: str, 
    payment_channel_service: PaymentChannelService = Depends(get_payment_channel),
    ):
    data = payment_channel_service.update_status(id, 0)
    if data:
        return ResponseUtils.success({
            "id": id,
            "name": data.name,
            "config": data.config,
            "is_enabled": data.status == 1,
            "updated_time": data.update_at,
        })
    return ResponseUtils.success(data={})

@router.put("/info")
async def payment_channel_config(
    id: str, 
    payment_channel_service: PaymentChannelService = Depends(get_payment_channel),
    body: dict = Body(..., description="支付渠道配置"),
    ):
    config = body.get("config")
    if config:
        data = payment_channel_service.update_config(id=id,config=config)
        if data:
            return ResponseUtils.success({
                "id": id,
                "name": data.name,
                "config": data.config,
                "is_enabled": data.status == 1,
                "updated_time": data.update_at,
            })
        return ResponseUtils.success(data={})
    return ResponseUtils.success(data={})
