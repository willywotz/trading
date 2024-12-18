import glob
import decimal
import pandas as pd
from wallet import *

def to_decimal(value: str):
    return decimal.Decimal(value)

class Bot:
    fee: decimal.Decimal = to_decimal("0")
    gap: decimal.Decimal = to_decimal("0.005") # 0.5%
    min_amount: decimal.Decimal = to_decimal("5")

    wallet: Wallet = None
    last_price: decimal.Decimal = None

    def __init__(self, wallet: Wallet):
        self.wallet = wallet

    # def next(self, price: decimal.Decimal):
    #     #check wallet port value more than min_amount + fee
    #     if self.wallet.port_value(price) < self.min_amount * (1 + self.fee):
    #         raise NotEnoughBalance("port value")

    #     # reset balance
    #     if self.last_price is None:
    #         quantity = self.find_min_quantity(price)

    #         if self.wallet.balance_coin < quantity:
    #             # self.wallet.buy(quantity, price)
    #             a = self.wallet.balance_base - (self.wallet.balance_coin * price)
    #             b = a / price / 2
    #             self.wallet.buy(b, price)
    #         elif self.wallet.balance_base < self.min_amount:
    #             # raise NotEnoughBalance("base")
    #             a = (self.wallet.balance_coin * price) - self.wallet.balance_base
    #             b = a / price / 2
    #             self.wallet.sell(b, price)
    #             # raise NotEnoughBalance("base")

    #         return self.set_last_price(price)

    #     # check last action price far from gap
    #     elif abs(self.last_price - price) < (self.last_price * self.gap):
    #         return

    #     quantity = self.find_quantity(price)

    #     try:
    #         if self.last_price - price < 0:
    #             self.wallet.sell(quantity, price)
    #         else:
    #             self.wallet.buy(quantity, price)
    #     except NotEnoughBalance:
    #         self.set_last_price(None)
    #         return self.next(price)

    #     return self.set_last_price(price)

    def next(self, price: decimal.Decimal):
        diff_quantity = (self.wallet.balance_coin - (self.wallet.balance_base / price)) / 2
        min_quantity = self.find_min_quantity(price)

        if self.last_price is not None \
            and abs(self.last_price - price) < (self.last_price * self.gap):
            return

        if abs(diff_quantity) > min_quantity:
            if diff_quantity > 0:
                self.wallet.sell(diff_quantity, price)
            else:
                self.wallet.buy(abs(diff_quantity), price)
            self.set_last_price(price)

    def set_fee(self, fee: decimal.Decimal):
        self.fee = fee
        self.wallet.fee = fee

    def set_gap(self, gap: decimal.Decimal):
        self.gap = gap

    def set_last_price(self, price: decimal.Decimal):
        self.last_price = price

    def find_min_quantity(self, price: decimal.Decimal):
        ndigit = len(f"{int(price)}")
        quantity = self.min_amount / price
        quantity = round(quantity, ndigit)

        while (quantity * price) < self.min_amount:
            quantity += pow(to_decimal("10"), -ndigit)

        return quantity

    def find_quantity(self, price: decimal.Decimal):
        return self.find_min_quantity(price)

    def force_sell(self, price: decimal.Decimal):
        ndigit = len(f"{int(price)}")
        quantity = round(self.wallet.balance_coin / 2, ndigit)
        self.wallet.sell(quantity, price)

if __name__ == "__main__":
    wallet = Wallet()
    wallet.balance_base = to_decimal("1000")

    bot = Bot(wallet=wallet)
    bot.set_fee(to_decimal("0.001")) # fee 0.1% per trade
    bot.set_gap(to_decimal("0.004")) # price gap 0.5%

    for file in glob.glob("klines/*.csv")[-1:]:
        df = pd.read_csv(file, converters={'close': to_decimal})
        for price in df['close']: bot.next(price)
