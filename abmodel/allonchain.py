"""
This model describes an approach to tokenizing deposits where ALL transactions and balances are
handled by smart-contracts. It assumes all participating banks and the central bank are on the
same blockchain.

Side note:  Technically, you can track the balance of all accounts through a single contract. But 
that would mean all accounts are in the same place, which is probably not desirable. Therefore, each
bank tracks it's customers in a contract and the banks interact at a higher-level through the central 
bank contract.
"""

import mesa
import random
from tqdm import tqdm

from abmodel.agents import Customer
from abmodel.abis import deploy_contracts
from simular import PyEvm, create_many_accounts

## HELPERS ##


def token_to_dollar(value):
    """
    Convert token to dollar
    """
    if value <= 0:
        return 0
    return value / 10**6


## REPORTERS ##


def b0_balance(model):
    return token_to_dollar(model.banks["B0"].totalSupply.call())


def b1_balance(model):
    return token_to_dollar(model.banks["B1"].totalSupply.call())


def b2_balance(model):
    return token_to_dollar(model.banks["B2"].totalSupply.call())


def central_bank_balance(model):
    return token_to_dollar(model.banks["centralbank"].totalSupply.call())


## MODEL ##


class BankingModel(mesa.Model):
    """
    Goal: have agents interact with banks.  track bank and central bank balances
    over time.

    Graphically display the invariant: sum(bank balances) always equals sum(central bank accounts)
    """

    def __init__(self, evm, num_customers=10, num_banks=3, num_steps=1000):
        super().__init__()
        self.num_banks = num_banks
        self.num_steps = num_steps
        self.num_customers = num_customers

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(40, 40, True)

        # create accounts
        customers = create_many_accounts(evm, num_customers)

        # deploy bank vaults
        self.banks = deploy_contracts(evm, num_banks)

        # create agents, attach to banks, and open customer accounts
        id = 1
        banks_as_list = list(self.banks.keys())
        banks_as_list.remove("centralbank")
        for wallet in customers:
            random_bank_symbol = random.choice(banks_as_list)
            agent = Customer(id, wallet, random_bank_symbol, self)
            self.schedule.add(agent)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

            id += 1

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "B0": b0_balance,
                "B1": b1_balance,
                "B2": b2_balance,
                "CENTRALBANK": central_bank_balance,
            }
        )

        self.running = True
        self.datacollector.collect(self)

    def deposit(self, bank_symbol, customer, amount):
        b = self.banks[bank_symbol]
        owner = b.owner.call()
        b.deposit.transact(customer, amount, caller=owner)

    def withdraw(self, bank_symbol, customer, amount):
        b = self.banks[bank_symbol]
        owner = b.owner.call()
        b.withdraw.transact(customer, amount, caller=owner)

    def step(self):
        # tell all the agents in the model to run their step function
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self):
        for _i in tqdm(range(self.num_steps)):
            self.step()


if __name__ == "__main__":
    evm = PyEvm()
    model = BankingModel(evm)
    model.run_model()
    df = model.datacollector.get_model_vars_dataframe()
    df["BANK_TOTALS"] = df["B0"] + df["B1"] + df["B2"]
    print(df)
