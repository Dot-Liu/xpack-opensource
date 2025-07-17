class ResponseUtils:

    @staticmethod
    def success(data=None, message="success", code=200):
        return {"code": str(code), "error_message": message, "data": data}

    @staticmethod
    def success_page(data=None, message="success", code=200, page_num=0, page_size=0, total=0):
        return {
            "code": str(code),
            "error_message": message,
            "data": data,
            "page": {"page": page_num, "page_size": page_size, "total": total},
        }

    @staticmethod
    def error(message="error", code=500, data=None, error_msg=None):
        if error_msg and isinstance(error_msg, dict):
            code = error_msg.get("code", code)
            message = error_msg.get("message", message)
        return {"code": str(code), "error_message": message, "data": data}
