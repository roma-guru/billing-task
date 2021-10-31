create type transaction_type as enum('transfer', 'deposit', 'withdrawal');

create table wallets(id serial primary key, username varchar(255), balance money default 0 check (balance>=0::money));
create table transactions(id serial primary key, from_id int references wallets(id), to_id int references wallets(id),
    amount money, ts timestamptz default current_timestamp, comment text default null, type transaction_type default 'transfer');
