class ResponseUtils:
    
    @staticmethod
    def success(data=None, message="success", code=200):
        return {
            "code": code,
            "message": message,
            "data": data
        }

    @staticmethod
    def error(message="error", code=1, data=None):
        return {
            "code": code,
            "message": message,
            "data": data
        }
