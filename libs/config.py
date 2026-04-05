class Config:
    class Generic:
        SUCCESS = (0, "Success", 200)
        API_FAIL = (1, "Some error occurred. Please try again later", 500)
        FAILURE = (1, "Our System are down, We are working on fixes. Please try after sometime.", 500)
        BAD_REQUEST = (1, "Bad request", 400)

        FILE_UPLOAD_FAIL = (3, "File couldn't be uploaded due to some error. Please try again later", 400)

        UNAUTHORIZED = (1, "Unauthorized", 401)
        PERMISSION_DENIED = (1, "Permission denied to access content", 403)
        TOKEN_EXPIRY = (1, "Token Expired", 401)
        INVALID_JWT_TOKEN = (1, "Invalid jwt Token", 401)