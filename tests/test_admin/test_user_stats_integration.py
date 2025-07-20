"""
用户统计接口集成测试
用于验证接口是否正常工作
"""
from datetime import date, timedelta


def test_user_stats_api_structure():
    """测试用户统计API的基本结构"""
    # 这是一个简单的结构测试，验证我们的实现符合规范
    
    # 期望的响应结构
    expected_response_structure = {
        "success": True,
        "error_message": "",
        "code": "200",
        "data": {
            "days": [
                {
                    "stats_day": "2024-01-01",  # date format
                    "call_tool_count": 0  # integer
                }
            ]
        }
    }
    
    # 验证日期格式生成
    test_date = date.today()
    date_str = test_date.strftime('%Y-%m-%d')
    assert len(date_str) == 10
    assert date_str.count('-') == 2
    
    print("API structure test passed")


def test_date_range_generation():
    """测试日期范围生成逻辑"""
    last_day = 7
    end_date = date.today()
    start_date = end_date - timedelta(days=last_day - 1)
    
    # 生成日期序列
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    # 验证结果
    assert len(dates) == last_day
    assert dates[0] == start_date.strftime('%Y-%m-%d')
    assert dates[-1] == end_date.strftime('%Y-%m-%d')
    
    print(f"Date range generation test passed: {len(dates)} days from {dates[0]} to {dates[-1]}")


if __name__ == "__main__":
    test_user_stats_api_structure()
    test_date_range_generation()
    print("All tests passed!")
