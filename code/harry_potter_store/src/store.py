from copy import deepcopy
from typing import Dict


class Store:
    book_types = ["1", "2", "3", "4", "5"]

    def __init__(self, book_price=8):
        self.book_price = book_price
        pass

    def _validate(self, to_buy_books: Dict[str, int]):
        for book_type, amount in to_buy_books.items():
            if book_type not in Store.book_types:
                raise ValueError("Book type %s must be in %s".format(book_type, Store.book_types))
            if amount <= 0:
                raise ValueError("Book amount %s for type %s must be > 0".format(amount, book_type))

    def _clean(self, to_buy_books: Dict[str, int]) -> dict:
        return dict(filter(lambda item: item[1] > 0 and item[0] in Store.book_types, to_buy_books.items()))

    def _decrement(self, to_buy_books: Dict[str, int], count: int) -> dict:
        first_part = {book: amount - 1 for book, amount in list(to_buy_books.items())[:count]}
        second_part = dict(list(to_buy_books.items())[count:])
        first_part.update(second_part)
        return self._clean(first_part)

    def _discount_wrapper(self, number, discount):
        return lambda to_buy_books, price, predicate: \
            self._discount(to_buy_books, price, predicate, number, discount)

    def _discount(self, to_buy_books, price, predicate, number, discount):
        if predicate(len(to_buy_books), number):
            price += number * self.book_price * (1 - discount)
            to_buy_books = self._decrement(to_buy_books, number)
        return to_buy_books, price

    def get_price(self, to_buy_books: Dict[str, int]) -> float:
        """
        to_buy_books - dictionary from book type and book amount
        key of dict -- book type
        value of dict -- book amount
        """
        self._validate(to_buy_books)
        to_buy_books = {k: v for k, v in sorted(to_buy_books.items(), key=lambda item: item[1])}
        discounts = [self._discount_wrapper(5, 0.25), self._discount_wrapper(4, 0.2),
                     self._discount_wrapper(3, 0.1), self._discount_wrapper(2, 0.05)]
        min_price = self.book_price * sum(to_buy_books.values())
        for i in range(len(discounts)):
            min_price = min(min_price,
                            self._get_price(to_buy_books,
                                            [discounts[i]], len(discounts) - i, lambda x, y: x >= y))
            min_price = min(min_price,
                            self._get_price(to_buy_books,
                                            discounts[0:i + 1], len(discounts) - i, lambda x, y: x == y))
        return min_price

    def _get_price(self, to_buy_books: Dict[str, int],
                   discount_funcs: list, min_value: int, predicate) -> float:
        """
        to_buy_books - dictionary from book type and book amount
        key of dict -- book type
        value of dict -- book amount
        discount_funcs - functions for calculate discount
        min_value - value for return from loop
        predicate - predicate for discount function
        """
        to_buy_books = deepcopy(to_buy_books)
        price = 0
        while len(to_buy_books) > min_value:
            for discount_func in discount_funcs:
                to_buy_books, price = discount_func(to_buy_books, price, predicate)

        count = sum(to_buy_books.values())
        return price + self.book_price * count
