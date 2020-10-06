pragma solidity 0.4.24;

contract Unique {
    function uniquify(uint[] input) public pure returns(uint[]) {
        uint length = input.length;
        if (length > 1) {
            uint b;
            uint cindex = 0;
            uint s;

            for (uint i = 0; i < length; i++) {
                s = 1 << (input[i] & 65535);
                if ((s & b) == 0) {
                    b |= s;
                    input[cindex++] = input[i];
                }
            }
            if (cindex != length) {
                return split(input, cindex);
            } 
        }
        return input;
    }

    function split(uint[] input, uint cindex) internal pure returns(uint[]) {
        uint[] memory ret = new uint[](cindex);
        for (uint j = 0; j < cindex; j++) {
            ret[j] = input[j];
        }
        return ret;
    }
}

// 0xE82D5B10ad98d34dF448b07a5a62C1aFfBEf758F
// 335083

