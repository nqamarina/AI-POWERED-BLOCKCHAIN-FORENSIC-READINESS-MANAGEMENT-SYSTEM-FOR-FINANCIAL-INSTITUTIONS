// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EvidenceStore {
    // A record structure to hold forensic data
    struct Record {
        string evidenceHash;
        uint256 timestamp;
    }

    // A list of all fraud records detected by the AI
    Record[] public forensicLedger;

    // Function for the AI to call when it finds fraud
    function storeEvidence(string memory _hash) public {
        forensicLedger.push(Record(_hash, block.timestamp));
    }

    // Function to see how many records we have
    function getRecordCount() public view returns (uint256) {
        return forensicLedger.length;
    }
}