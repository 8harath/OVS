// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title VoterRegistry
 * @dev Track voter eligibility and voting status on blockchain
 * @notice Prevents double-voting at the smart contract level
 */
contract VoterRegistry is Ownable {

    // Mapping: voter address => election ID => has voted
    mapping(address => mapping(uint256 => bool)) public hasVoted;

    // Mapping: voter address => is eligible to vote
    mapping(address => bool) public isEligible;

    // Mapping: voter ID hash => wallet address (for lookup)
    mapping(bytes32 => address) public voterIdToAddress;

    // Count of eligible voters
    uint256 public eligibleVoterCount;

    // Events
    event VoterRegistered(address indexed voter, bytes32 voterIdHash);
    event VoterRemoved(address indexed voter);
    event VoteCast(address indexed voter, uint256 indexed electionId, uint256 timestamp);
    event VotersRegisteredBatch(uint256 count);

    /**
     * @dev Constructor - sets the contract deployer as the initial owner
     */
    constructor() Ownable(msg.sender) {}

    /**
     * @dev Register a voter as eligible
     * @param _voter Voter's wallet address
     * @param _voterIdHash Hashed voter ID (for privacy)
     */
    function registerVoter(address _voter, bytes32 _voterIdHash) external onlyOwner {
        require(_voter != address(0), "Invalid voter address");
        require(_voterIdHash != bytes32(0), "Invalid voter ID hash");
        require(!isEligible[_voter], "Voter already registered");

        isEligible[_voter] = true;
        voterIdToAddress[_voterIdHash] = _voter;
        eligibleVoterCount++;

        emit VoterRegistered(_voter, _voterIdHash);
    }

    /**
     * @dev Remove a voter's eligibility
     * @param _voter Voter's wallet address
     */
    function removeVoter(address _voter) external onlyOwner {
        require(isEligible[_voter], "Voter not registered");

        isEligible[_voter] = false;
        eligibleVoterCount--;

        emit VoterRemoved(_voter);
    }

    /**
     * @dev Mark voter as having voted in an election
     * @param _voter Voter's wallet address
     * @param _electionId Election ID
     */
    function markAsVoted(address _voter, uint256 _electionId) external onlyOwner {
        require(isEligible[_voter], "Voter not eligible");
        require(!hasVoted[_voter][_electionId], "Voter already voted");
        require(_electionId > 0, "Invalid election ID");

        hasVoted[_voter][_electionId] = true;
        emit VoteCast(_voter, _electionId, block.timestamp);
    }

    /**
     * @dev Check if voter has voted in an election
     * @param _voter Voter's wallet address
     * @param _electionId Election ID
     * @return True if voter has already voted
     */
    function checkHasVoted(address _voter, uint256 _electionId)
        external
        view
        returns (bool)
    {
        return hasVoted[_voter][_electionId];
    }

    /**
     * @dev Check if voter is eligible
     * @param _voter Voter's wallet address
     * @return True if voter is eligible
     */
    function checkIsEligible(address _voter) external view returns (bool) {
        return isEligible[_voter];
    }

    /**
     * @dev Get voter address from hashed voter ID
     * @param _voterIdHash Hashed voter ID
     * @return Voter's wallet address
     */
    function getVoterAddress(bytes32 _voterIdHash) external view returns (address) {
        return voterIdToAddress[_voterIdHash];
    }

    /**
     * @dev Batch register multiple voters (gas optimization)
     * @param _voters Array of voter addresses
     * @param _voterIdHashes Array of hashed voter IDs
     */
    function batchRegisterVoters(
        address[] memory _voters,
        bytes32[] memory _voterIdHashes
    ) external onlyOwner {
        require(_voters.length == _voterIdHashes.length, "Array lengths must match");
        require(_voters.length > 0, "Empty batch");
        require(_voters.length <= 100, "Batch too large");

        for (uint256 i = 0; i < _voters.length; i++) {
            if (!isEligible[_voters[i]] && _voters[i] != address(0)) {
                isEligible[_voters[i]] = true;
                voterIdToAddress[_voterIdHashes[i]] = _voters[i];
                eligibleVoterCount++;
                emit VoterRegistered(_voters[i], _voterIdHashes[i]);
            }
        }

        emit VotersRegisteredBatch(_voters.length);
    }

    /**
     * @dev Get total number of eligible voters
     * @return Number of eligible voters
     */
    function getTotalEligibleVoters() external view returns (uint256) {
        return eligibleVoterCount;
    }

    /**
     * @dev Check voter status for an election
     * @param _voter Voter address
     * @param _electionId Election ID
     * @return isEligibleToVote Whether voter is eligible
     * @return hasAlreadyVoted Whether voter has already voted
     */
    function getVoterStatus(address _voter, uint256 _electionId)
        external
        view
        returns (bool isEligibleToVote, bool hasAlreadyVoted)
    {
        return (isEligible[_voter], hasVoted[_voter][_electionId]);
    }

    /**
     * @dev Get contract version
     */
    function version() external pure returns (string memory) {
        return "1.0.0";
    }
}
