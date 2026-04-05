from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Constant:
    SERVICE_NAME = "DJANGO_SAMPLE_PROJECT"


    class TimeInSeconds:
        THIRTY = 30

        class Weeks:
            THREE = 1814400

        class Days:
            TWO = 172800
            THREE = 259200
            FIVE = 432000
            SIX = 518400
            SEVEN = 604800

        class Hours:
            TWELVE = 43200
            TWENTY_FOUR = 86400

        class Seconds:
            FIVE = 5
            TEN = 10
            FIFTEEN = 15
            THIRTY = 30

        class Minutes:
            ONE = 60
            TWO = 120
            FOUR = 240
            FIVE = 300
            SIX = 360
            SEVEN = 420
            TEN = 600
            FIFTEEN = 900
            SEVENTEEN = 1020
            TWENTY = 1200
            TWENTY_FIVE = 1500
            THIRTY = 1800
            FORTY = 2400
            SIXTY = 3600
            NINETY = 5400
            HUNDRED = 6000

    class RequestMethod:
        POST = "POST"
        GET = "GET"
        PUT = "PUT"
        PATCH = "PATCH"
        DELETE = "DELETE"

    class HttpStatusCode:
        class Success(BaseEnum):
            OK = 200
            CREATED = 201
            ACCEPTED = 202
            NO_CONTENT = 204

        class Redirection(BaseEnum):
            MULTIPLE_CHOICE = 300
            MOVED_PERMANENTLY = 301

        class ClientError(BaseEnum):
            BAD_REQUEST = 400
            UNAUTHORIZED = 401
            FORBIDDEN = 403
            NOT_FOUND = 404
            CONFLICT = 409

        class ServerError(BaseEnum):
            INTERNAL_SERVER_ERROR = 500
            BAD_GATEWAY = 502
            SERVICE_UNAVAILABLE = 503
            GATEWAY_TIMEOUT = 504
            HTTP_VERSION_NOT_SUPPORTED = 505

        class Verification(BaseEnum):
            VERIFICATION_FAILED = 422

    class AuthenticationType:
        SERVICE_AUTH = "SERVICE_AUTH"
        USER_AUTH = "USER_AUTH"
        CLIENT_AUTH = "CLIENT_AUTH"
        PUBLIC_AUTH = "PUBLIC_AUTH"
        MERCHANT_AUTH = "MERCHANT_AUTH"

    class ENV:
        PRODUCTION = "PRODUCTION"
        STAGING = "STAGING"
        LOCAL = "LOCAL"
        UAT = "UAT"

    class RequestServiceCallType:
        INCOMING = "INCOMING"
        OUTGOING = "OUTGOING"

    class ExceptionPriority:
        LOW = "LOW"
        MEDIUM = "MEDIUM"
        HIGH = "HIGH"

    class RequestServiceType:
        THIRD_PARTY = "THIRD_PARTY"
        MICROSERVICE = "MICROSERVICE"

    class RequestService:
        pass


    class Events:
        pass

    class Partner:
        pass

    class Vendor:
        pass

    class AlertWebhook:
        MEDIUM_PRIORITY = ""
        API_RESPONSE = ""
        TESTING = ""
        FLOW = ""
        KAFKA = ""
        CRON = ""

    class Numeric:
        TWENTY_THOUSAND = 20000
        FORTY_THOUSAND = 40000
        TEN_LAKH = 1000000
        TWENTY_LAKH = 2000000


