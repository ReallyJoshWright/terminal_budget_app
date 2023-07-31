PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

drop table if exists balance;

Create Table balance(
  id INTEGER PRIMARY KEY,
  initial_balance FLOAT,
  date TEXT
);

COMMIT;
