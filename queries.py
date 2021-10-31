# Wallets
get_wallet_by_id = "select id,username,balance::numeric from wallets where id=%(id)s"
get_all_wallets = "select id,username from wallets"
create_wallet = "insert into wallets(username,balance) values (%(username)s,%(balance)s) returning id"
clear_wallets = "delete from wallets"
increase_wallet_balance = "update wallets set balance=balance+%(amount)s::money where id=%(id)s"
decrease_wallet_balance = "update wallets set balance=balance-%(amount)s::money where id=%(id)s"

# Transactions
get_transaction_by_id = "select id,from_id,to_id,amount::numeric,ts,comment,type from transactions where id=%(id)s"
get_transactions_by_wallet = "select id,from_id,to_id,amount::numeric,ts,comment,type from transactions where from_id=%(wallet_id)s or to_id=%(wallet_id)s"
clear_transactions = "delete from transactions"
create_transaction = "insert into transactions(from_id,to_id,amount,comment,type) values (%(from_id)s,%(to_id)s,%(amount)s,%(comment)s,%(type)s) returning id"

# Need explicitly set isolation level
# https://github.com/aio-libs/aiopg/issues/699#issuecomment-699940524
set_isolation_level = "set transaction isolation level serializable"

