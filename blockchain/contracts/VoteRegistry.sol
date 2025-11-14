// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title VoteRegistry
 * @dev Store cryptographic hashes of votes on blockchain for immutability and verification
 * @notice This contract stores vote hashes, NOT the actual votes, preserving voter privacy
 */
contract VoteRegistry is Ownable, ReentrancyGuard, Pausable {

    struct Vote {
        bytes32 voteHash;           // Cryptographic hash of vote (anonymized)
        uint256 electionId;         // Election identifier
        uint256 timestamp;          // Block timestamp when vote was recorded
        string referenceNumber;     // Unique reference for verification
        bool exists;                // Flag to check if vote exists
    }

    // Mapping from reference number to vote details
    mapping(string => Vote) public votes;

    // Mapping from election ID to total vote count
    mapping(uint256 => uint256) public electionVoteCount;

    // Array of all reference numbers (for enumeration)
    string[] public allVotes;

    // Events
    event VoteRecorded(
        string indexed referenceNumber,
        bytes32 voteHash,
        uint256 indexed electionId,
        uint256 timestamp
    );

    event ElectionVoteIncremented(
        uint256 indexed electionId,
        uint256 newCount
    );

    event VoteBatchRecorded(
        uint256 batchSize,
        uint256 indexed electionId
    );

    /**
     * @dev Record a single vote on the blockchain
     * @param _voteHash Cryptographic hash of the vote
     * @param _electionId Election identifier
     * @param _referenceNumber Unique reference for this vote
     */
    function recordVote(
        bytes32 _voteHash,
        uint256 _electionId,
        string memory _referenceNumber
    ) external whenNotPaused nonReentrant {

        // Validation
        require(!votes[_referenceNumber].exists, "Vote already recorded");
        require(_voteHash != bytes32(0), "Invalid vote hash");
        require(bytes(_referenceNumber).length > 0, "Invalid reference number");
        require(_electionId > 0, "Invalid election ID");

        // Create vote record
        votes[_referenceNumber] = Vote({
            voteHash: _voteHash,
            electionId: _electionId,
            timestamp: block.timestamp,
            referenceNumber: _referenceNumber,
            exists: true
        });

        // Add to enumeration
        allVotes.push(_referenceNumber);

        // Increment election vote count
        electionVoteCount[_electionId]++;

        // Emit events
        emit VoteRecorded(_referenceNumber, _voteHash, _electionId, block.timestamp);
        emit ElectionVoteIncremented(_electionId, electionVoteCount[_electionId]);
    }

    /**
     * @dev Record multiple votes in a single transaction (gas optimization)
     * @param _voteHashes Array of vote hashes
     * @param _electionIds Array of election IDs
     * @param _referenceNumbers Array of reference numbers
     */
    function recordVoteBatch(
        bytes32[] memory _voteHashes,
        uint256[] memory _electionIds,
        string[] memory _referenceNumbers
    ) external whenNotPaused nonReentrant {

        // Validate array lengths match
        require(
            _voteHashes.length == _electionIds.length &&
            _voteHashes.length == _referenceNumbers.length,
            "Array lengths must match"
        );

        require(_voteHashes.length > 0, "Empty batch");
        require(_voteHashes.length <= 50, "Batch too large"); // Prevent gas limit issues

        // Process each vote
        for (uint256 i = 0; i < _voteHashes.length; i++) {
            require(!votes[_referenceNumbers[i]].exists, "Duplicate vote in batch");
            require(_voteHashes[i] != bytes32(0), "Invalid vote hash");
            require(bytes(_referenceNumbers[i]).length > 0, "Invalid reference");

            votes[_referenceNumbers[i]] = Vote({
                voteHash: _voteHashes[i],
                electionId: _electionIds[i],
                timestamp: block.timestamp,
                referenceNumber: _referenceNumbers[i],
                exists: true
            });

            allVotes.push(_referenceNumbers[i]);
            electionVoteCount[_electionIds[i]]++;

            emit VoteRecorded(
                _referenceNumbers[i],
                _voteHashes[i],
                _electionIds[i],
                block.timestamp
            );
        }

        emit VoteBatchRecorded(_voteHashes.length, _electionIds[0]);
    }

    /**
     * @dev Verify a vote exists and get its details
     * @param _referenceNumber The reference number to verify
     * @return voteHash The cryptographic hash of the vote
     * @return electionId The election ID
     * @return timestamp When the vote was recorded
     * @return exists Whether the vote exists
     */
    function verifyVote(string memory _referenceNumber)
        external
        view
        returns (
            bytes32 voteHash,
            uint256 electionId,
            uint256 timestamp,
            bool exists
        )
    {
        Vote memory vote = votes[_referenceNumber];
        return (
            vote.voteHash,
            vote.electionId,
            vote.timestamp,
            vote.exists
        );
    }

    /**
     * @dev Get total number of votes recorded across all elections
     * @return Total number of votes
     */
    function getTotalVotes() external view returns (uint256) {
        return allVotes.length;
    }

    /**
     * @dev Get vote reference number by index (for enumeration)
     * @param index Index in the allVotes array
     * @return referenceNumber The reference number at that index
     */
    function getVoteByIndex(uint256 index)
        external
        view
        returns (string memory referenceNumber)
    {
        require(index < allVotes.length, "Index out of bounds");
        return allVotes[index];
    }

    /**
     * @dev Get vote count for a specific election
     * @param _electionId The election ID
     * @return Vote count for that election
     */
    function getElectionVoteCount(uint256 _electionId)
        external
        view
        returns (uint256)
    {
        return electionVoteCount[_electionId];
    }

    /**
     * @dev Emergency pause - only owner can call
     * @notice Prevents new votes from being recorded
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause the contract - only owner can call
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Get contract version
     */
    function version() external pure returns (string memory) {
        return "1.0.0";
    }
}
