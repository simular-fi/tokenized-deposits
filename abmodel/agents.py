import mesa
import random


MAX_VALUE = 10000


class Customer(mesa.Agent):
    """
    Bank customer.
    """

    def __init__(self, uid, wallet, banksymbol, model):
        super().__init__(uid, model)
        self.wallet = wallet
        self.banksymbol = banksymbol
        self.model = model

        # open account
        bank = self.model.banks[banksymbol]
        bank.openAccount.transact(caller=wallet)

    def move(self):
        """
        Move around the grid
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()

        action = self.random.choice(["d", "w", "x"])
        if action == "d":
            # make a deposit
            amount = random.randint(1, MAX_VALUE) * 10**6
            self.model.deposit(self.banksymbol, self.wallet, amount)

        elif action == "w":
            # get their bank and make a withdraw
            bank = self.model.banks[self.banksymbol]
            balance = bank.balanceOf.call(self.wallet)

            if balance > 0:
                amount = random.randint(1, balance)
                self.model.withdraw(self.banksymbol, self.wallet, amount)
        else:
            bank = self.model.banks[self.banksymbol]
            balance = bank.balanceOf.call(self.wallet)
            if balance > 0:
                amount = random.randint(1, balance)

                # find another agent to pay...
                cellies = self.model.grid.get_cell_list_contents([self.pos])
                # don't pick myself
                cellies.pop(cellies.index(self))

                if len(cellies) > 0:
                    other = self.random.choice(cellies)

                    if other.banksymbol == self.banksymbol:
                        # inner bank transfer
                        bank.transfer.transact(other.wallet, amount, caller=self.wallet)
                    else:
                        recipient_bank_address = self.model.banks[
                            other.banksymbol
                        ].address

                        centralbank = self.model.banks["centralbank"]
                        owner = bank.owner.call()

                        centralbank.approve.transact(
                            recipient_bank_address, amount, caller=owner
                        )

                        bank.makeTransfer.transact(
                            recipient_bank_address,
                            self.wallet,
                            other.wallet,
                            amount,
                            caller=owner,
                        )
