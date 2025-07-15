class ResponseUtils:

    @staticmethod
    def success(data=None, message="success", code=200):
        return {"code": code, "message": message, "data": data}

    @staticmethod
    def success_page(data=None, message="success", code=200, page_num=0, page_size=0, total=0):
        return {"code": code, "message": message, "data": data, "pagination": {"page": page_num, "page_size": page_size, "total": total}}

    @staticmethod
    def error(message="error", code=1, data=None):
        return {"code": code, "message": message, "data": data}
