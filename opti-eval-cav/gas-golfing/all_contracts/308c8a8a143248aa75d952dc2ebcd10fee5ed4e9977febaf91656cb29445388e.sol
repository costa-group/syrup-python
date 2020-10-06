pragma solidity 0.4.24;

contract IndexOf {
    function indexOf(string haystackString, string needleString) public pure returns (int) {
        // Boyer-Moore does better with longer needles; @TODO: tune this number?
        if (bytes(needleString).length > 8) {
            return boyerMoore(bytes(haystackString), bytes(needleString));
        }
        return naive(bytes(haystackString), bytes(needleString));
    }

    // See: https://en.wikipedia.org/wiki/Boyer–Moore_string-search_algorithm
    // See: https://www.geeksforgeeks.org/pattern-searching-set-7-boyer-moore-algorithm-bad-character-heuristic/
    function boyerMoore(bytes haystack, bytes needle) internal pure returns (int) {
        uint haystackLength = haystack.length;
        uint needleLength = needle.length;

        // Trivial case
        if(needleLength > haystackLength) { return -1; }

        uint i;
        int j;

        // Create a bad cahracter map, offset by 1 (so we can use uint256)
        uint[256] memory badCharacter;
        for (i = 0; i < needleLength; i++) {
            badCharacter[uint(needle[i])] = i + 1;
        }

        uint shift = 0;
        uint end = haystackLength - needleLength;
        while (shift <= end) {
            j = int(needleLength - 1);
            while (true) {

               // Found a match!
               if (j < 0) { return int(shift); }

               if (needle[uint(j)] != haystack[uint(int(shift) + j)]) {
                   break;
               }
               j--;
            }

            // Shift! (j is non-negatibe)
            uint value = badCharacter[uint(haystack[shift + uint(j)])] - 1;
            if (int(value) < j) {
                shift += uint(j) - value;
            } else {
                shift += 1;
            }
        }

        return -1;
    }

    function naive(bytes haystack, bytes needle) internal pure returns (int) {

        uint haystackLength = haystack.length;
        uint needleLength = needle.length;

        if(needleLength > haystackLength) { return -1; }

        uint end = haystackLength - needleLength + 1;
        for (uint i = 0; i < end; i++) {
            uint found = 1;
            for (uint j = 0; j < needleLength; j++) {
                if (haystack[i + j] != needle[j]) {
                    found = 0;
                    break;
                }
            }

            if (found == 1) {
                return int(i);
            }
        }

        return -1;
    }
}

