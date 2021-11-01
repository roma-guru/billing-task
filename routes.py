from decimal import Decimal

from starlette.responses import Response
from starlette.routing import Route

from exceptions import NotEnoughMoney, NotFound
from repository import TransactionRepository, WalletRepository


async def create_wallet(request):
    form = await request.json()
    repo = WalletRepository(request.app.state.pg_pool)
    wallet_id = await repo.create(form["username"])
    wallet = await repo.get_by_id(wallet_id)
    return Response(wallet.json(), media_type="application/json")


async def get_all_wallets(request):
    repo = WalletRepository(request.app.state.pg_pool)
    wallets = await repo.get_all()
    resp = ",".join([obj.json() for obj in wallets])
    return Response(f"[{resp}]", media_type="application/json")


async def get_wallet(request):
    repo = WalletRepository(request.app.state.pg_pool)
    wallet_id = request.path_params["id"]
    try:
        wallet = await repo.get_by_id(wallet_id)
    except NotFound:
        return Response("not found", 404)
    return Response(wallet.json(), media_type="application/json")


wallet_routes = [
    Route("/", create_wallet, methods=["post"]),
    Route("/", get_all_wallets),
    Route("/{id:int}", get_wallet),
]


async def get_transaction(request):
    repo = TransactionRepository(request.app.state.pg_pool)
    trans_id = request.path_params["id"]
    try:
        trans = await repo.get_by_id(trans_id)
    except NotFound:
        return Response("not found", 404)
    return Response(trans.json(), media_type="application/json")


async def get_transactions_by_wallet(request):
    repo = TransactionRepository(request.app.state.pg_pool)
    wallet_id = request.path_params["wallet_id"]
    transactions = await repo.get_by_wallet(wallet_id)
    resp = ",".join([obj.json() for obj in transactions])
    return Response(f"[{resp}]", media_type="application/json")


async def make_deposit(request):
    repo = TransactionRepository(request.app.state.pg_pool)
    form = await request.json()
    try:
        trans_id = await repo.make_deposit(form["to_id"], Decimal(form["amount"]))
    except ValueError:
        return Response("bad parameters", 400)

    trans_obj = await repo.get_by_id(trans_id)
    return Response(trans_obj.json(), media_type="application/json")


async def make_transfer(request):
    repo = TransactionRepository(request.app.state.pg_pool)
    form = await request.json()
    try:
        trans_id = await repo.make_transfer(
            form["from_id"], form["to_id"], Decimal(form["amount"])
        )
    except ValueError:
        return Response("bad parameters", 400)
    except NotEnoughMoney:
        return Response("not enough money!", 400)

    trans_obj = await repo.get_by_id(trans_id)
    return Response(trans_obj.json(), media_type="application/json")


transaction_routes = [
    Route("/by/{wallet_id:int}", get_transactions_by_wallet),
    Route("/{id:int}", get_transaction),
    Route("/transfer", make_transfer, methods=["post"]),
    Route("/deposit", make_deposit, methods=["post"]),
]
