"""
用户统计服务测试
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from services.admin_service.services.user_stats_service import UserStatsService
from services.common.models.user_apikey import UserApiKey
from services.common.models.mcp_call_log import McpCallLog


class TestUserStatsService:
    """用户统计服务测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.db_mock = Mock(spec=Session)
        self.service = UserStatsService(self.db_mock)
        
    def test_get_apikey_call_tool_stats_success(self):
        """测试成功获取API密钥调用统计"""
        # 准备测试数据
        apikey_id = "test-apikey-id"
        last_day = 3
        
        # Mock API密钥存在
        mock_apikey = Mock(spec=UserApiKey)
        mock_apikey.id = apikey_id
        self.db_mock.query.return_value.filter.return_value.first.return_value = mock_apikey
        
        # Mock统计查询结果
        mock_stats_row = Mock()
        mock_stats_row.stats_day = date.today() - timedelta(days=1)
        mock_stats_row.call_tool_count = 5
        
        query_mock = self.db_mock.query.return_value
        query_mock.join.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_stats_row]
        
        # 执行测试
        result = self.service.get_apikey_call_tool_stats(apikey_id, last_day)
        
        # 验证结果
        assert len(result) == last_day
        assert all("stats_day" in item and "call_tool_count" in item for item in result)
        
        # 验证包含有数据的日期
        yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_data = next((item for item in result if item["stats_day"] == yesterday_str), None)
        assert yesterday_data is not None
        assert yesterday_data["call_tool_count"] == 5
        
        # 验证包含无数据的日期（应该为0）
        today_str = date.today().strftime('%Y-%m-%d')
        today_data = next((item for item in result if item["stats_day"] == today_str), None)
        assert today_data is not None
        assert today_data["call_tool_count"] == 0
        
    def test_get_apikey_call_tool_stats_invalid_apikey(self):
        """测试无效的API密钥ID"""
        # Mock API密钥不存在
        self.db_mock.query.return_value.filter.return_value.first.return_value = None
        
        # 执行测试，预期抛出ValueError
        with pytest.raises(ValueError, match="Invalid apikey_id"):
            self.service.get_apikey_call_tool_stats("invalid-apikey", 7)
            
    def test_get_apikey_call_tool_stats_empty_result(self):
        """测试没有调用记录的情况"""
        # Mock API密钥存在
        mock_apikey = Mock(spec=UserApiKey)
        self.db_mock.query.return_value.filter.return_value.first.return_value = mock_apikey
        
        # Mock空的统计结果
        query_mock = self.db_mock.query.return_value
        query_mock.join.return_value.filter.return_value.group_by.return_value.all.return_value = []
        
        # 执行测试
        result = self.service.get_apikey_call_tool_stats("test-apikey", 5)
        
        # 验证结果 - 应该返回5天，每天调用次数都是0
        assert len(result) == 5
        assert all(item["call_tool_count"] == 0 for item in result)
        
    def test_get_apikey_call_tool_stats_default_last_day(self):
        """测试默认last_day参数"""
        # Mock API密钥存在
        mock_apikey = Mock(spec=UserApiKey)
        self.db_mock.query.return_value.filter.return_value.first.return_value = mock_apikey
        
        # Mock空的统计结果
        query_mock = self.db_mock.query.return_value
        query_mock.join.return_value.filter.return_value.group_by.return_value.all.return_value = []
        
        # 执行测试（不传last_day参数）
        result = self.service.get_apikey_call_tool_stats("test-apikey")
        
        # 验证结果 - 应该返回30天（默认值）
        assert len(result) == 30
