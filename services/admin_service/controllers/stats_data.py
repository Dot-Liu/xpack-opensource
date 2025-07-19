from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.models.user import User
from services.common.models.user_wallet import UserWallet
from services.common.models.mcp_service import McpService
from services.common.models.mcp_call_log import McpCallLog

router = APIRouter()


@router.get("/platform")
async def get_platform_overview(db: Session = Depends(get_db)):
    """Get platform overview statistics and metrics."""
    try:
        # 获取总用户数（非管理员且未删除）
        total_user = db.query(User).filter(User.role_id != 1, User.is_deleted == 0).count()  # 非管理员 (role_id 1 是管理员)  # 未删除

        # 获取总余额
        total_balance_result = db.query(func.sum(UserWallet.balance)).scalar()
        total_balance = int(total_balance_result) if total_balance_result else 0

        # 获取服务总数
        total_service = db.query(McpService).count()

        # 获取今天的调用量
        today = date.today()
        today_invoke_count = db.query(McpCallLog).filter(func.date(McpCallLog.created_at) == today).count()

        # 构建响应数据
        response_data = {
            "total_user": total_user,
            "total_balance": total_balance,
            "total_service": total_service,
            "invoke_count": {"today": today_invoke_count},
        }

        return ResponseUtils.success(response_data)

    except Exception as e:
        return ResponseUtils.error(f"获取平台概览失败: {str(e)}", 500)
