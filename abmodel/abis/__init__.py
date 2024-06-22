from pathlib import Path
from simular import contract_from_raw_abi, create_many_accounts, create_account, PyEvm

PATH = Path(__file__).parent


def centralbank_contract(evm):
    with open(f"{PATH}/../../out/CentralBank.sol/CentralBank.json") as f:
        full = f.read()
    return contract_from_raw_abi(evm, full)


def bankvault_contract(evm):
    with open(f"{PATH}/../../out/BankVault.sol/BankVault.json") as f:
        full = f.read()
    return contract_from_raw_abi(evm, full)


def deploy_contracts(evm, num_banks=3):
    """
    Creates central bank and bank owner accounts
    Deploys the central bank
    Deploys N number of banks. 3 by default
    Returns a dict with the information
    """
    data = {}
    cbowner = create_account(evm)
    cb = centralbank_contract(evm)
    cbaddress = cb.deploy(caller=cbowner)
    data["centralbank"] = cb.at(cbaddress)

    # create bank owner accounts
    banksowner_accounts = create_many_accounts(evm, num_banks)

    # deploy the banks and return the contracts ready to go
    for i, bo in enumerate(banksowner_accounts):
        bc = bankvault_contract(evm)
        bank_symbol = f"B{i}"
        baddress = bc.deploy(cbaddress, f"Bank{i}", bank_symbol, caller=bo)
        data[bank_symbol] = bc.at(baddress)

    return data


def do_deploy():
    evm = PyEvm()
    data = deploy_contracts(evm)

    print(data)
