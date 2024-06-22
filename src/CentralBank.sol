// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.13;

import {ERC20} from "solmate/tokens/ERC20.sol";

/// Represent a Central Bank that tokenizes Bank deposits.
///
/// FOR EXPERIMENTATION ONLY! NOT AN AUDITED, SAFE CONTRACT!
contract CentralBank is ERC20 {
    address public owner;

    /// Support 6 decimal places. $1 == 1000000
    constructor() ERC20("centralbank", "CB", 6) {
        owner = msg.sender;
    }

    /// Called by a Bank to mint tokens for deposits
    function mint(uint256 value) external {
        _mint(msg.sender, value);
    }

    /// Called by a Bank to burn tokens on a withdraw
    function burn(uint256 value) external {
        _burn(msg.sender, value);
    }
}
