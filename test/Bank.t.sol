// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

import {BankVault} from "../src/BankVault.sol";
import {CentralBank} from "../src/CentralBank.sol";

contract BankTest is Test {
    // 2 banks in the network
    BankVault public bankA;
    BankVault public bankB;

    CentralBank public centralBank;

    // bankers (owners)
    address bankerA = address(0x11);
    address bankerB = address(0x12);

    // bankA customers
    address bob = address(0x13);
    address tony = address(0x14);

    // bankB customers
    address alice = address(0x15);

    // amount(s)
    uint256 FIVE = 5e6;
    uint256 TEN = 10e6;

    function setUp() public {
        centralBank = new CentralBank();

        vm.prank(bankerA);
        bankA = new BankVault(centralBank, "BankA", "BA");

        vm.prank(bankerB);
        bankB = new BankVault(centralBank, "BankB", "BB");

        // note: account owners must call with their wallet
        vm.prank(bob);
        bankA.openAccount();

        vm.prank(tony);
        bankA.openAccount();

        vm.prank(alice);
        bankB.openAccount();
    }

    // test helper
    // a vault's total balance == balance of it's account at the central bank
    function _check_invariant(BankVault bank) internal view {
        assertEq(bank.totalSupply(), centralBank.balanceOf(address(bank)));
    }

    function test_deposit_withdraw() public {
        // bob deposits 10
        vm.prank(bankerA);
        bankA.deposit(bob, TEN);

        _check_invariant(bankA);
        assertEq(TEN, bankA.balanceOf(bob));

        // bob withdraws 5
        vm.prank(bankerA);
        bankA.withdraw(bob, FIVE);

        _check_invariant(bankA);
        assertEq(FIVE, bankA.balanceOf(bob));
    }

    function test_transfer_within_same_bank() public {
        // Bob sends 5 to tony
        vm.prank(bankerA);
        bankA.deposit(bob, TEN);

        // HACK: Bob must sign transfers!
        vm.prank(bob);
        bankA.transfer(tony, FIVE);

        assertEq(FIVE, bankA.balanceOf(bob));
        assertEq(FIVE, bankA.balanceOf(tony));
        assertEq(TEN, centralBank.totalSupply());
        _check_invariant(bankA);
    }

    function test_interbank_transfer() public {
        // Setup: Bob sends 5 to alice at BankB
        vm.prank(bankerA);
        bankA.deposit(bob, TEN);

        // approve the recipient bank to transfer amount
        //vm.prank(address(bankA));
        //assert(centralBank.approve(address(bankB), FIVE));

        // send money to bank B for alice
        vm.prank(bankerA);
        bankA.makeTransfer(address(bankB), bob, alice, FIVE);

        assertEq(FIVE, bankA.balanceOf(bob));
        assertEq(FIVE, bankB.balanceOf(alice));
        assertEq(TEN, centralBank.totalSupply());

        _check_invariant(bankA);
        _check_invariant(bankB);
    }
}
