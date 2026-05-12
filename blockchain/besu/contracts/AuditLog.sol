// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * AuditLog.sol  —  ClimateSmartTriage
 * -------------------------------------
 * Immutable on-chain record of every health data access event.
 * Deployed on a private Hyperledger Besu network operated by ITDA Paderu.
 *
 * This contract does NOT store health records.
 * It stores only: hashed DID, access type, purpose, and timestamp.
 * The DID is hashed so it cannot be mapped to an individual
 * without the original identifier.
 */

contract AuditLog {

    struct AccessEvent {
        bytes32 didHash;
        string  accessType;
        string  purpose;
        uint256 timestamp;
    }

    AccessEvent[] private _log;

    event DataAccessed(
        bytes32 indexed didHash,
        string  accessType,
        string  purpose,
        uint256 timestamp
    );

    /**
     * Record a data access event.
     * Called by the ClimateSmartTriage backend on every read or write.
     */
    function recordAccess(
        string memory did,
        string memory accessType,
        string memory purpose
    ) external {
        bytes32 didHash = keccak256(abi.encodePacked(did));
        _log.push(AccessEvent(didHash, accessType, purpose, block.timestamp));
        emit DataAccessed(didHash, accessType, purpose, block.timestamp);
    }

    function totalEvents() external view returns (uint256) {
        return _log.length;
    }

    function getEvent(uint256 index) external view returns (
        bytes32 didHash,
        string memory accessType,
        string memory purpose,
        uint256 timestamp
    ) {
        require(index < _log.length, "Index out of range");
        AccessEvent storage ev = _log[index];
        return (ev.didHash, ev.accessType, ev.purpose, ev.timestamp);
    }
}
