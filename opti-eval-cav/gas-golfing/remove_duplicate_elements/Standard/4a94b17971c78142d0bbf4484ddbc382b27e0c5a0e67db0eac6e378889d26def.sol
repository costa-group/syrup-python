/**
 * This file is part of the 1st Solidity Gas Golfing Contest.
 *
 * This work is licensed under Creative Commons Attribution ShareAlike 3.0.
 * https://creativecommons.org/licenses/by-sa/3.0/
 */

pragma solidity 0.4.24;

contract Unique {

    function uniquify(uint[] input) public pure returns(uint[] ret) {
        uint len = input.length;
        if (len <= 1) {
            return input;
        }
        uint lenny = 13 * len / 7;
        if (lenny % 2 == 0) {
            lenny++;
        }

        uint ptr;
        uint value = 1;
        uint valueMod;
        uint tempRet;
        uint i;
        ret = new uint[](lenny);

        // loop while i == ptr
        for(; i < len; i++) {
            value = valueMod = input[i] + 1;
            while(true) {
                valueMod %= lenny;
                tempRet = ret[valueMod];
                if (tempRet == value) {
                    i += lenny;
                    break;
                }
                if (tempRet == 0) {
                    ret[valueMod] = value;
                    break;
                }
                valueMod+=value;
            }
        }

        if (i == len) {
            return input;
        }

        i -= lenny;

        ptr = i - 1;

        // new loop once i != ptr
        for(; i < len; i++) {
            value = valueMod = input[i] + 1;
            while(true) {
                valueMod %= lenny;
                tempRet = ret[valueMod];
                if (tempRet == value) break;
                if (tempRet == 0) {
                    ret[valueMod] = value;
                    input[ptr] = value - 1;
                    ptr++;
                    break;
                }
                valueMod+=value;
            }
        }

        ret = new uint[](ptr);

        for(i = 0; i < ptr; i++) {
            ret[i] = input[i];
        }

        return ret;
    }

}

