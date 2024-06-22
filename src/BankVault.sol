// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.13;

import {CentralBank} from "./CentralBank.sol";
import {ERC20} from "solmate/tokens/ERC20.sol";
import {SafeTransferLib} from "solmate/utils/SafeTransferLib.sol";

/// A Bank Vault that manages customer accounts and interacts
/// with a CentralBank.
///
/// FOR EXPERIMENTATION ONLY! NOT AN AUDITED, SAFE CONTRACT!
contract BankVault is ERC20 {
    using SafeTransferLib for CentralBank;

    /// owner of the bank
    address public owner;
    /// pointer to central bank contract
    CentralBank public immutable centralBank;

    /// Mapping to track account holders for this bank
    mapping(address => bool) private customers;

    event Deposit(
        address indexed bank,
        address indexed onBehalfOf,
        uint256 amount
    );

    event Withdraw(
        address indexed bank,
        address indexed onBehalfOf,
        uint256 amount
    );

    constructor(
        CentralBank _centralBank,
        string memory _name,
        string memory _symbol
    ) ERC20(_name, _symbol, _centralBank.decimals()) {
        owner = msg.sender;
        centralBank = _centralBank;
    }

    function _isAccountHolder(address customer) private view returns (bool) {
        return customers[customer];
    }

    /// Open an account for the customer. Assumes the customer has a
    /// wallet with the bank.
    function openAccount() external {
        require(!_isAccountHolder(msg.sender), "Already a customer");

        customers[msg.sender] = true;
        approve(address(this), type(uint256).max);
    }

    /// Make a deposit on behalf of a customer.  Tokenizing the deposit.
    ///
    function deposit(address recipient, uint256 amount) external {
        require(msg.sender == owner, "Not the bank owner");
        require(_isAccountHolder(recipient), "Not a customer of this bank");

        // mint shares to recipient to track their balance in the vault
        _mint(recipient, amount);

        // mint tokens on central bank
        centralBank.mint(amount);

        emit Deposit(address(this), recipient, amount);
    }

    /// Make a withdraw on behalf of the customer
    function withdraw(address from, uint256 amount) external {
        require(msg.sender == owner, "Not the bank owner");

        _burn(from, amount);
        centralBank.burn(amount);

        emit Withdraw(address(this), from, amount);
    }

    /// Interbank payment...
    function makeTransfer(
        address bank,
        address from,
        address recipient,
        uint256 amount
    ) external {
        require(msg.sender == owner, "Not the bank owner");
        _burn(from, amount);
        centralBank.approve(bank, amount);
        BankVault(bank).receiveTransfer(recipient, amount);
    }

    /// Called when from a bank that wants to transfer funds to *this* vault
    ///
    /// Interbank transfers are made on the central bank
    function receiveTransfer(address recipient, uint256 amount) external {
        require(_isAccountHolder(recipient), "Not a customer of this bank");

        _mint(recipient, amount);
        centralBank.safeTransferFrom(msg.sender, address(this), amount);
    }
}
