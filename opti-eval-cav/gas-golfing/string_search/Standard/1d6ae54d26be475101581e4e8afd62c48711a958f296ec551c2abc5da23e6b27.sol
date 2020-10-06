pragma solidity 0.4.24;

contract IndexOf {
    function indexOf(
        string haystack,
        string needle
    ) public pure returns(int) {
        bytes memory hsBytes = bytes(haystack);
        bytes memory nBytes = bytes(needle);
        if (nBytes.length == 0) {
            return 0;
        }
        if (hsBytes.length < nBytes.length) {
            return -1;
        }
        if (nBytes.length == 1) {
            return findOne(hsBytes, nBytes[0]);
        }
        return findMuch(hsBytes, nBytes);
    }

    function findOne(
        bytes hsBytes,
        byte nByte
    ) private pure returns (int) {
        int i;
        while (uint(i) < hsBytes.length) {
            if (hsBytes[uint(i++)] == nByte) {
                return i-1;
            }
        }
        return -1;
    }

    function findMuch(
        bytes hsBytes,
        bytes nBytes
    ) private pure returns (int h) {
        int hsLen = int(hsBytes.length);
        int nLen = int(nBytes.length);
        int flag = hsLen-(nLen-1);
        int n;
        while (h < flag) {
            if (hsBytes[uint(h)] != nBytes[0]) {
                h += 1;
                continue;
            }
            n = nLen - 1;
            while (true) {
                if (hsBytes[uint(h)+uint(n)] != nBytes[uint(n)]) { break; }
                if (--n == 0) { return; }
            }
            n = 0;
            while (true) {
                if (nBytes[uint(n)] == hsBytes[uint(h)+uint(nLen)]) { break; }
                if (++n == nLen) { break; }
            }
            if (n != nLen) {
                h += nLen - n;
                continue;
            }
            h += nLen;
        }
        return -1;
    }
}
