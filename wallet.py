from decimal import Decimal

class NotEnoughBalance(Exception): ...

class Wallet:
    fee: Decimal = Decimal("0")

    balance_coin: Decimal = Decimal("0")
    balance_base: Decimal = Decimal("0")

    volume: Decimal = Decimal("0")

    def buy(self, quantity: Decimal, price: Decimal):
        amount = quantity * price * (1 + self.fee)

        if self.balance_base < amount:
            raise NotEnoughBalance("base")

        before = f"{self.balance_coin:.5f} {self.balance_base:.2f}"

        self.balance_coin += quantity
        self.balance_base -= amount
        self.volume += quantity * price

        after = f"{self.balance_coin:.5f} {self.balance_base:.2f}"

        print(f"price: {price:.2f}, before: {before}, after: {after}, port_value: {self.port_value(price):.2f}, volume: {self.volume:.2f}, amount: {quantity * price:.2f}")

    def sell(self, quantity: Decimal, price: Decimal):
        if self.balance_coin < quantity:
            raise NotEnoughBalance("coin")

        before = f"{self.balance_coin:.5f} {self.balance_base:.2f}"

        self.balance_coin -= quantity
        self.balance_base += quantity * price * (1 - self.fee)
        self.volume += quantity * price

        after = f"{self.balance_coin:.5f} {self.balance_base:.2f}"

        print(f"price: {price:.2f}, before: {before}, after: {after}, port_value: {self.port_value(price):.2f}, volume: {self.volume:.2f}, amount: {quantity * price:.2f}")

    def port_value(self, price: Decimal):
        return (self.balance_coin * price) + self.balance_base
