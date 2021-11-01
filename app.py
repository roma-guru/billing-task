import aiopg
from starlette.applications import Starlette
from starlette.routing import Mount

from config import DEBUG, DSN
from routes import transaction_routes, wallet_routes


async def init_db():
    app.state.pg_pool = await aiopg.create_pool(DSN)


def close_db():
    app.state.pg_pool.close()


routes = [
    Mount("/v1/wallets", routes=wallet_routes),
    Mount("/v1/transactions", routes=transaction_routes),
]
app = Starlette(
    debug=DEBUG, on_startup=[init_db], on_shutdown=[close_db], routes=routes
)
