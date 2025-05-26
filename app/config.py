AUTH_HEADER = "Token"

JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRES_MINUTES = 15
JWT_REFRESH_EXPIRES_DAYS = 7
JWT_JTI_LEN = 10
SECRET_KEY = "changeme"

API_PREFIX = "/api"
LOGIN_URI = "/auth/login"
REGISTER_URI = "/auth/register"
REFRESH_TOKEN_URI = "/auth/refresh"
METRICS_URI = "/metrics"
VALUES_URI = "/metrics/{metric_id}/values"
