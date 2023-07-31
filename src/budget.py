import sys
import os
import csv
import sqlite3
import argparse
from datetime import datetime

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
CONFIG_DIR = os.path.abspath(os.path.join(ROOT_DIR, "config"))
FILES_DIR = os.path.abspath(os.path.join(ROOT_DIR, "files"))
sys.path.append(ROOT_DIR)

TRANSACTION = 0
MERCHANT = 1
AMOUNT = 2
DATE = 3


class Budget:
    def __init__(self, args):
        self.args = args
        self.conn = sqlite3.connect(CONFIG_DIR + "/account.db")
        self.cursor = self.conn.cursor()

        self.get_args()

        self.conn.close()

    def get_args(self):
        args = [self.args.file, self.args.initial_balance, self.args.ret_bal,
                self.args.transactions, self.args.credits, self.args.debits,
                self.args.spending]
        if args == [None, None, None, None, None, None, None]:
            initial_balance = self.get_initial_balance()
            balance = self.get_balance()
            print("Initial Balance: ", initial_balance)
            print("Balance: ", balance)

        if self.args.file is not None:
            data = self.read_csv(self.args.file)
            self.add_to_database(data)
        if self.args.initial_balance is not None:
            self.set_initial_balance(self.args.initial_balance)
        if self.args.transactions is not None:
            if self.args.credits is not None:
                self.get_transactions(self.args.transactions, True, False)
            elif self.args.debits is not None:
                self.get_transactions(self.args.transactions, False, True)
            else:
                self.get_transactions(self.args.transactions, False, False)
        if self.args.ret_bal is not None:
            initial_balance = self.get_initial_balance()
            balance = self.get_balance()
            print("Initial Balance: ", initial_balance)
            print("Balance: ", balance)
        if self.args.spending is not None:
            self.get_spending()

    def get_spending(self):
        m = "merchant"
        n = "# of times received payment"
        t = "total amount received"
        p = "% of total credits"

        print("\nCredits:")
        print(f"{'-'*95}")
        print(f"| {m:16s} | {n:15s} | {t:15s} | {p:10s} |")
        print(f"|{'-'*18}|{'-'*29}|{'-'*23}|{'-'*20}|")

        query_sum_total_credits = f"SELECT SUM(amount) AS sum FROM account \
                WHERE transaction_type = 'credit';"
        self.cursor.execute(query_sum_total_credits)
        sum_total_credits_result = self.cursor.fetchone()
        sum_total_credits = sum_total_credits_result[0]

        query_count_credits = f"SELECT merchant, COUNT(merchant) FROM account \
                GROUP BY merchant HAVING transaction_type = 'credit';"
        self.cursor.execute(query_count_credits)
        count_credits_result = self.cursor.fetchall()

        for i in count_credits_result:
            query_sum_credits = f"SELECT SUM(amount) AS sum FROM account \
                    WHERE merchant = '{i[0]}';"
            self.cursor.execute(query_sum_credits)
            sum_credits = self.cursor.fetchall()
            for j in sum_credits:
                percent = (j[0] / sum_total_credits) * 100
                percent = round(percent, 2)

                part1 = f"| {i[0]:16s} | {str(i[1]):27s} | {str(j[0]):21s} |"
                part2 = f" {str(percent):18s} |"
                print(part1 + part2)

        print(f"{'-'*95}")

        nd = "# of times spent money"
        td = "total amount spent"
        pd = "% of total debits"

        print("\nDebits:")
        print(f"{'-'*86}")
        print(f"| {m:16s} | {nd:15s} | {td:15s} | {pd:10s} |")
        print(f"|{'-'*18}|{'-'*24}|{'-'*20}|{'-'*19}|")

        query_sum_total_debits = f"SELECT SUM(amount) AS sum FROM account \
                WHERE transaction_type = 'debit';"
        self.cursor.execute(query_sum_total_debits)
        sum_total_debits_result = self.cursor.fetchone()
        sum_total_debits = sum_total_debits_result[0]

        query_count_debits = f"SELECT merchant, COUNT(merchant) FROM account \
                GROUP BY merchant HAVING transaction_type = 'debit';"
        self.cursor.execute(query_count_debits)
        count_debits_result = self.cursor.fetchall()

        for i in count_debits_result:
            query_sum_debits = f"SELECT SUM(amount) AS sum FROM account \
                    WHERE merchant = '{i[0]}';"
            self.cursor.execute(query_sum_debits)
            sum_debits = self.cursor.fetchall()
            for j in sum_debits:
                percent = (j[0] / sum_total_debits) * 100
                percent = round(percent, 2)

                part1d = f"| {i[0]:16s} | {str(i[1]):22s} | {str(j[0]):18s} |"
                part2d = f" {str(percent):17s} |"
                print(part1d + part2d)

        print(f"{'-'*86}")

    def get_transactions(self, n, credit_only, debit_only):
        if credit_only:
            query = f"SELECT * FROM account WHERE transaction_type = 'credit' \
                    ORDER BY date DESC LIMIT {n};"
        elif debit_only:
            query = f"SELECT * FROM account WHERE transaction_type = 'debit' \
                    ORDER BY date DESC LIMIT {n};"
        else:
            query = f"SELECT * FROM account ORDER BY date DESC LIMIT {n};"
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        t = "Transaction Type"
        m = "Merchant"
        a = "Amount"
        d = "Date"

        print(f"{'-'*69}")
        print(f"| {t:16s} | {m:15s} | {a:15s} | {d:10s} |")
        print(f"|{'-'*18}|{'-'*17}|{'-'*17}|{'-'*12}|")
        for i in result:
            p1 = f"| {i[1]:16s} | {i[2]:15s} | {str(i[3]):15s} |"
            p2 = f" {i[4]:10s} |"
            print(p1 + p2)
        print(f"{'-'*69}")

    def set_initial_balance(self, initial_balance):
        now = datetime.now()
        query = f"INSERT INTO balance (initial_balance, date) VALUES \
                ({initial_balance}, '{now}');"
        self.cursor.execute(query)
        self.conn.commit()

    def get_initial_balance(self):
        query = f"SELECT initial_balance FROM balance ORDER BY date DESC \
                LIMIT 1;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return 0

    def get_balance(self):
        query = f"SELECT SUM(amount) AS sum_amount FROM account;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is None:
            return 0
        else:
            if result[0] is None:
                balance = 0
            else:
                balance = result[0]
            initial_balance = self.get_initial_balance()
            return round(initial_balance + balance, 2)

    def read_csv(self, filename):
        data = []
        with open(os.path.join(FILES_DIR + "/" + filename), "r") as file:
            csv_file = csv.reader(file)
            for lines in csv_file:
                data.append(lines)
        return data

    def add_to_database(self, data):
        for record in data:
            query = f"INSERT INTO account (transaction_type, merchant, \
                    amount, date) VALUES \
                    ('{record[TRANSACTION]}', \
                    '{record[MERCHANT]}', {record[AMOUNT]}, \
                    '{record[DATE]}');"
            self.cursor.execute(query)
        self.conn.commit()


def main():
    parser = argparse.ArgumentParser(description=
                                     "An app to manage your budget")
    parser.add_argument("-f", action="store", default=None,
                        dest="file", required=False, help="Pass a csv file")
    parser.add_argument("-B", action="store", default=None,
                        dest="initial_balance", required=False,
                        help="Enter an initial balance")
    parser.add_argument("-b", action="store_true", default=None,
                        dest="ret_bal", required=False,
                        help="Returns only your balance")
    parser.add_argument("-n", action="store", default=None,
                        dest="transactions", required=False,
                        help="Number of transactions")
    parser.add_argument("-c", action="store_true", default=None,
                        dest="credits", required=False,
                        help="Returns only credits")
    parser.add_argument("-d", action="store_true", default=None,
                        dest="debits", required=False,
                        help="Returns only debits")
    parser.add_argument("-g", action="store_true", default=None,
                        dest="spending", required=False,
                        help="Returns spending info")
    args = parser.parse_args()
    Budget(args)


if __name__ == "__main__":
    main()
