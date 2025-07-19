"""
MCP调用记录仓储类
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from services.common.models.mcp_call_log import McpCallLog, ProcessStatus


class McpCallLogRepository:
    """MCP调用记录仓储类"""
    
    def __init__(self, db: Session):
        self.db = db

    def create(self, call_log: McpCallLog) -> McpCallLog:
        """
        创建MCP调用记录
        
        Args:
            call_log: MCP调用记录对象
            
        Returns:
            McpCallLog: 创建的记录
        """
        self.db.add(call_log)
        self.db.commit()
        self.db.refresh(call_log)
        return call_log

    def get_by_id(self, log_id: str) -> Optional[McpCallLog]:
        """
        根据ID获取MCP调用记录
        
        Args:
            log_id: 记录ID
            
        Returns:
            Optional[McpCallLog]: 记录对象，不存在则返回None
        """
        return self.db.query(McpCallLog).filter(McpCallLog.id == log_id).first()

    def update_status(self, log_id: str, status: ProcessStatus, error_msg: Optional[str] = None, wallet_history_id: Optional[str] = None) -> bool:
        """
        更新处理状态
        
        Args:
            log_id: 记录ID
            status: 新状态
            error_msg: 错误信息（可选）
            wallet_history_id: 关联的钱包历史记录ID（可选）
            
        Returns:
            bool: 更新是否成功
        """
        log_record = self.get_by_id(log_id)
        if log_record:
            log_record.process_status = status
            if error_msg:
                log_record.error_msg = error_msg
            if wallet_history_id:
                log_record.wallet_history_id = wallet_history_id
            self.db.commit()
            return True
        return False

    def get_user_call_history(self, user_id: str, page: int = 1, page_size: int = 20) -> tuple[int, List[McpCallLog]]:
        """
        获取用户调用历史
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            tuple[int, List[McpCallLog]]: (总数, 记录列表)
        """
        total = self.db.query(McpCallLog).filter(McpCallLog.user_id == user_id).count()
        
        offset = (page - 1) * page_size
        records = (
            self.db.query(McpCallLog)
            .filter(McpCallLog.user_id == user_id)
            .order_by(McpCallLog.call_start_time.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        return total, records

    def get_pending_logs(self, limit: int = 100) -> List[McpCallLog]:
        """
        获取待处理的记录
        
        Args:
            limit: 最大数量
            
        Returns:
            List[McpCallLog]: 待处理记录列表
        """
        return (
            self.db.query(McpCallLog)
            .filter(McpCallLog.process_status == ProcessStatus.PENDING)
            .order_by(McpCallLog.created_at.asc())
            .limit(limit)
            .all()
        )
