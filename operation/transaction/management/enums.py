from enum import Enum


class MethodOfTransaction(Enum):
    ATM = 'ATM/Cash'
    WIRE = 'Wire Transfer'
    ONLINE = 'Online Transfer'
    CHECK = 'Check'
    MONEY_ORDER = 'Money Order'


class SpendingCategory(Enum):
    UTILITIES = 'Utilities'
    GROCERIES = 'Groceries'
    ENTERTAINMENT = 'Entertainment'
    DINING = 'Dining'
    TRAVEL = 'Travel'
    MEDICAL = 'Medical'
