// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ElectionManager
 * @dev Manage election lifecycle on blockchain
 * @notice Tracks election status and validity on-chain
 */
contract ElectionManager is Ownable {

    struct Election {
        uint256 id;
        string title;
        uint256 startTime;
        uint256 endTime;
        bool isActive;
        bool exists;
        uint256 createdAt;
    }

    // Mapping from election ID to election details
    mapping(uint256 => Election) public elections;

    // Array of all election IDs (for enumeration)
    uint256[] public allElections;

    // Events
    event ElectionCreated(
        uint256 indexed electionId,
        string title,
        uint256 startTime,
        uint256 endTime,
        uint256 createdAt
    );

    event ElectionActivated(uint256 indexed electionId, uint256 timestamp);
    event ElectionDeactivated(uint256 indexed electionId, uint256 timestamp);
    event ElectionUpdated(uint256 indexed electionId, string title);

    /**
     * @dev Constructor - sets the contract deployer as the initial owner
     */
    constructor() Ownable(msg.sender) {}

    /**
     * @dev Create a new election on the blockchain
     * @param _electionId Unique identifier for the election
     * @param _title Title/name of the election
     * @param _startTime Unix timestamp when voting starts
     * @param _endTime Unix timestamp when voting ends
     */
    function createElection(
        uint256 _electionId,
        string memory _title,
        uint256 _startTime,
        uint256 _endTime
    ) external onlyOwner {
        require(!elections[_electionId].exists, "Election already exists");
        require(_endTime > _startTime, "End time must be after start time");
        require(_startTime >= block.timestamp, "Start time must be in future");
        require(bytes(_title).length > 0, "Title cannot be empty");
        require(_electionId > 0, "Invalid election ID");

        elections[_electionId] = Election({
            id: _electionId,
            title: _title,
            startTime: _startTime,
            endTime: _endTime,
            isActive: false,
            exists: true,
            createdAt: block.timestamp
        });

        allElections.push(_electionId);

        emit ElectionCreated(_electionId, _title, _startTime, _endTime, block.timestamp);
    }

    /**
     * @dev Activate an election to allow voting
     * @param _electionId Election ID to activate
     */
    function activateElection(uint256 _electionId) external onlyOwner {
        require(elections[_electionId].exists, "Election does not exist");
        require(!elections[_electionId].isActive, "Election already active");
        require(
            block.timestamp >= elections[_electionId].startTime,
            "Election not yet started"
        );
        require(
            block.timestamp <= elections[_electionId].endTime,
            "Election has ended"
        );

        elections[_electionId].isActive = true;
        emit ElectionActivated(_electionId, block.timestamp);
    }

    /**
     * @dev Deactivate an election to stop voting
     * @param _electionId Election ID to deactivate
     */
    function deactivateElection(uint256 _electionId) external onlyOwner {
        require(elections[_electionId].exists, "Election does not exist");
        require(elections[_electionId].isActive, "Election not active");

        elections[_electionId].isActive = false;
        emit ElectionDeactivated(_electionId, block.timestamp);
    }

    /**
     * @dev Update election title
     * @param _electionId Election ID to update
     * @param _newTitle New title for the election
     */
    function updateElectionTitle(uint256 _electionId, string memory _newTitle)
        external
        onlyOwner
    {
        require(elections[_electionId].exists, "Election does not exist");
        require(bytes(_newTitle).length > 0, "Title cannot be empty");

        elections[_electionId].title = _newTitle;
        emit ElectionUpdated(_electionId, _newTitle);
    }

    /**
     * @dev Check if an election is currently ongoing
     * @param _electionId Election ID to check
     * @return True if election is active and within time bounds
     */
    function isElectionOngoing(uint256 _electionId) external view returns (bool) {
        Election memory election = elections[_electionId];

        if (!election.exists || !election.isActive) {
            return false;
        }

        return (block.timestamp >= election.startTime &&
                block.timestamp <= election.endTime);
    }

    /**
     * @dev Check if an election has ended
     * @param _electionId Election ID to check
     * @return True if current time is past election end time
     */
    function hasElectionEnded(uint256 _electionId) external view returns (bool) {
        require(elections[_electionId].exists, "Election does not exist");
        return block.timestamp > elections[_electionId].endTime;
    }

    /**
     * @dev Get election details
     * @param _electionId Election ID to query
     * @return id Election ID
     * @return title Election title
     * @return startTime Start timestamp
     * @return endTime End timestamp
     * @return isActive Whether election is active
     * @return exists Whether election exists
     */
    function getElection(uint256 _electionId)
        external
        view
        returns (
            uint256 id,
            string memory title,
            uint256 startTime,
            uint256 endTime,
            bool isActive,
            bool exists
        )
    {
        Election memory election = elections[_electionId];
        return (
            election.id,
            election.title,
            election.startTime,
            election.endTime,
            election.isActive,
            election.exists
        );
    }

    /**
     * @dev Get total number of elections created
     * @return Total number of elections
     */
    function getTotalElections() external view returns (uint256) {
        return allElections.length;
    }

    /**
     * @dev Get election ID by index
     * @param index Index in the allElections array
     * @return Election ID at that index
     */
    function getElectionIdByIndex(uint256 index) external view returns (uint256) {
        require(index < allElections.length, "Index out of bounds");
        return allElections[index];
    }

    /**
     * @dev Get contract version
     */
    function version() external pure returns (string memory) {
        return "1.0.0";
    }
}
