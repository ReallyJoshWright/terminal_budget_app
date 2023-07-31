PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

drop table if exists account;

Create Table account(
  id INTEGER PRIMARY KEY,
  transaction_type TEXT,
  merchant TEXT,
  amount FLOAT,
  date TEXT
);

COMMIT;
