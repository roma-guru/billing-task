import asyncio
import random
from dataclasses import dataclass
from decimal import Decimal
from typing import List

import aiopg
from psycopg2.errors import CheckViolation, SerializationFailure
from psycopg2.extras import DictCursor

from exceptions import NotEnoughMoney, NotFound
from models import Transaction, Wallet
from queries import (
    create_transaction,
    create_wallet,
    decrease_wallet_balance,
    get_all_wallets,
    get_transaction_by_id,
    get_transactions_by_wallet,
    get_wallet_by_id,
    increase_wallet_balance,
    set_isolation_level,
)


@dataclass
class WalletRepository:
    pool: aiopg.Pool

    async def create(self, username: str, balance: Decimal = Decimal(0)) -> int:
        with (await self.pool.cursor()) as cur:
            await cur.execute(create_wallet, {"username": username, "balance": balance})
            return (await cur.fetchone())[0]

    async def get_all(self) -> List[Wallet]:
        with (await self.pool.cursor()) as cur:
            await cur.execute(get_all_wallets)
            return [
                Wallet(id=id, username=username)
                for id, username in await cur.fetchall()
            ]

    async def get_by_id(self, id: int) -> Wallet:
        with (await self.pool.cursor()) as cur:
            await cur.execute(get_wallet_by_id, {"id": id})
            row = await cur.fetchone()
            if row is None:
                raise NotFound(str(id))
            id, username, balance = row
            return Wallet(id=id, username=username, balance=balance)


@dataclass
class TransactionRepository:
    pool: aiopg.Pool

    async def get_by_id(self, id: int) -> Transaction:
        with (await self.pool.cursor(cursor_factory=DictCursor)) as cur:
            await cur.execute(get_transaction_by_id, {"id": id})
            row = await cur.fetchone()
            if row is None:
                raise NotFound(str(id))
            return Transaction(**row)

    async def get_by_wallet(self, wallet_id: int) -> List[Transaction]:
        with (await self.pool.cursor(cursor_factory=DictCursor)) as cur:
            await cur.execute(get_transactions_by_wallet, {"wallet_id": wallet_id})
            return [Transaction(**row) for row in await cur.fetchall()]

    async def make_transfer(self, from_id: int, to_id: int, amount: Decimal) -> int:
        if from_id == to_id:
            raise ValueError("cant transfer to itself!")
        if amount <= 0:
            raise ValueError("amount must be positive!")

        with (await self.pool.cursor()) as cur:
            while True:
                try:
                    async with cur.begin():
                        await cur.execute(set_isolation_level)
                        await cur.execute(
                            increase_wallet_balance, {"id": to_id, "amount": amount}
                        )
                        await cur.execute(
                            decrease_wallet_balance, {"id": from_id, "amount": amount}
                        )
                        await cur.execute(
                            create_transaction,
                            {
                                "from_id": from_id,
                                "to_id": to_id,
                                "amount": amount,
                                "comment": f"transfer {from_id}->{to_id} of ${amount}",
                                "type": "transfer",
                            },
                        )
                        return (await cur.fetchone())[0]
                except SerializationFailure:
                    # just try again with random delay
                    await asyncio.sleep(random.random())
                except CheckViolation:
                    # not enough money by sender, so error
                    raise NotEnoughMoney(str(from_id))

    async def make_deposit(self, to_id: int, amount: Decimal) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive!")

        with (await self.pool.cursor()) as cur:
            while True:
                try:
                    async with cur.begin():
                        await cur.execute(set_isolation_level)
                        await cur.execute(
                            increase_wallet_balance, {"id": to_id, "amount": amount}
                        )
                        await cur.execute(
                            create_transaction,
                            {
                                "to_id": to_id,
                                "from_id": None,
                                "amount": amount,
                                "comment": f"deposit ->{to_id} of ${amount}",
                                "type": "deposit",
                            },
                        )
                        return (await cur.fetchone())[0]
                except SerializationFailure:
                    # just try again with random delay
                    await asyncio.sleep(random.random())

    # internal method for tests
    async def _create(
        self, from_id: int, to_id: int, amount: Decimal, comment: str, type: str
    ) -> int:
        with (await self.pool.cursor()) as cur:
            await cur.execute(
                create_transaction,
                {
                    "from_id": from_id,
                    "to_id": to_id,
                    "amount": amount,
                    "comment": comment,
                    "type": type,
                },
            )
            return (await cur.fetchone())[0]
