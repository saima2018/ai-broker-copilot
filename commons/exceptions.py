class BaseError(Exception):
    def __init__(self, status_code, code, message):
        self.status_code = status_code
        self.code = code
        self.message = message


class BadRequest(BaseError):
    """错误请求，错误码4000"""

    def __init__(self, message):
        super(BadRequest, self).__init__(status_code=400, code=4000, message=message)


class DownLoadError(BaseError):
    """资源下载失败，错误码4001"""

    def __init__(self, message):
        super(DownLoadError, self).__init__(status_code=400, code=4001, message=message)


class UnzipError(BaseError):
    """解压失败，错误码4002"""

    def __init__(self, message):
        super(UnzipError, self).__init__(status_code=400, code=4002, message=message)


class HaveLoadModel(BaseError):
    """设备已加载模型，错误码4003"""

    def __init__(self, message):
        super(HaveLoadModel, self).__init__(status_code=400, code=4003, message=message)


class NotLoadModel(BaseError):
    """设备未加载模型，错误码4004"""

    def __init__(self, message):
        super(NotLoadModel, self).__init__(status_code=400, code=4004, message=message)


class ResourceNotExist(BaseError):
    """资源不存在，错误码4005"""

    def __init__(self, message):
        super(ResourceNotExist, self).__init__(status_code=400, code=4005, message=message)


class ResourceReadError(BaseError):
    """资源读取失败，错误码4006"""

    def __init__(self, message):
        super(ResourceReadError, self).__init__(status_code=400, code=4006, message=message)


class ImageReadError(BaseError):
    """资源读取失败，错误码4006"""

    def __init__(self, message):
        super(ImageReadError, self).__init__(status_code=400, code=4007, message=message)


class InitializeError(BaseError):
    """设备初始化失败，错误码5001"""

    def __init__(self, message):
        super(InitializeError, self).__init__(status_code=500, code=5001, message=message)


class DeInitializeError(BaseError):
    """设备反初始化失败，错误码5002"""

    def __init__(self, message):
        super(DeInitializeError, self).__init__(status_code=500, code=5002, message=message)


class InferenceError(BaseError):
    """推理失败，错误码5003"""

    def __init__(self, message):
        super(InferenceError, self).__init__(status_code=500, code=5003, message=message)


class DataProcessError(BaseError):
    """数据预处理失败，错误码5003"""

    def __init__(self, message):
        super(DataProcessError, self).__init__(status_code=500, code=5004, message=message)


class DecodeError(BaseError):
    """解码失败，错误码5004"""

    def __init__(self, message):
        super(DecodeError, self).__init__(status_code=500, code=5005, message=message)


class InternalError(BaseError):
    """内部错误，错误码500"""

    def __init__(self, message):
        super(InternalError, self).__init__(status_code=500, code=500, message=message)

