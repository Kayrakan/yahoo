import os
OAUTHLIB_RELAX_TOKEN_SCOPE = "1"
SECRET = os.getenv("SECRET")
BROKER = os.getenv("REDISCLOUD_URL", "redis://localhost:6379")
RESULT_BACKEND = os.getenv("REDISCLOUD_URL", "redis://localhost:6379")