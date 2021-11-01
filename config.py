from starlette.config import Config

# Config will be read from environment variables and/or ".env" files.
config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
DSN = config("DSN")
