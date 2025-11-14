# Phase 1: Proof of Concept

**Duration:** 4-6 weeks
**Budget:** $10,000-20,000
**Status:** 🔴 Not Started

---

## Overview

This phase focuses on building the core blockchain infrastructure on Polygon Mumbai testnet and creating a basic integration with the existing Flask application. By the end of this phase, you'll have working smart contracts and the ability to record and verify votes on the blockchain.

### Goals

1. Deploy smart contracts to Polygon Mumbai testnet
2. Create Python blockchain service integration
3. Record test votes on blockchain
4. Verify votes from blockchain
5. Build admin dashboard for blockchain monitoring

### What You'll Have at the End

- ✅ 3 smart contracts deployed and tested on testnet
- ✅ Python `BlockchainService` class fully functional
- ✅ Updated Flask routes for blockchain voting
- ✅ Admin dashboard showing blockchain status
- ✅ 100+ successful test votes
- ✅ Complete documentation

### What's NOT in This Phase

- ❌ Production deployment
- ❌ Batch voting optimization
- ❌ Advanced privacy features
- ❌ Public audit interface
- ❌ Real user elections

---

## Prerequisites

### Team

- [ ] 1 Solidity Developer (full-time, 4-6 weeks)
- [ ] 1 Python/Flask Developer (full-time, 4-6 weeks)
- [ ] 1 QA Engineer (part-time, 2-3 weeks)

### Environment Setup

- [ ] Node.js 16+ installed
- [ ] Python 3.8+ installed
- [ ] Git repository access
- [ ] Code editor (VS Code recommended)

### Accounts & Access

- [ ] Polygon Mumbai testnet wallet created
- [ ] Testnet MATIC obtained (from faucet)
- [ ] Alchemy or Infura account created (free tier)
- [ ] PolygonScan Mumbai account (for verification)

### Knowledge

- [ ] Basic Solidity understanding
- [ ] Flask/Python proficiency
- [ ] Web3 concepts familiarity
- [ ] Git workflow knowledge

---

## Week-by-Week Plan

### Week 1: Setup & Smart Contract Development

**Goal:** Environment ready, smart contracts written

**Tasks:**
- Day 1-2: Development environment setup
- Day 3-5: Write smart contracts
- Day 4-5: Write unit tests for contracts

### Week 2: Smart Contract Deployment & Testing

**Goal:** Contracts deployed to testnet, verified and tested

**Tasks:**
- Day 1-2: Deploy contracts to Mumbai
- Day 3-4: Verify contracts on PolygonScan
- Day 5: Integration testing with web3.js

### Week 3: Backend Integration

**Goal:** Python blockchain service working

**Tasks:**
- Day 1-2: Create BlockchainService class
- Day 3-4: Update Flask routes
- Day 5: Database schema updates

### Week 4: Frontend Updates & Testing

**Goal:** UI updated, full end-to-end testing

**Tasks:**
- Day 1-2: Update vote templates
- Day 3: Create admin dashboard
- Day 4-5: End-to-end testing

### Week 5-6: Documentation & Polish

**Goal:** Everything documented, ready for demo

**Tasks:**
- Documentation
- Bug fixes
- Performance testing
- Demo preparation

---

## Detailed Implementation Steps

## Step 1: Environment Setup (Days 1-2)

### 1.1 Install Required Tools

```bash
# Node.js and npm (for Hardhat)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be 16+
npm --version

# Install Hardhat globally
npm install -g hardhat

# Python dependencies
pip install web3 python-dotenv eth-account
```

### 1.2 Create Blockchain Project Structure

```bash
cd /home/user/OVS

# Create blockchain directory
mkdir blockchain
cd blockchain

# Initialize Hardhat project
npx hardhat init
# Select: "Create a TypeScript project"

# Install dependencies
npm install --save-dev @nomicfoundation/hardhat-toolbox
npm install @openzeppelin/contracts
npm install dotenv
```

### 1.3 Configure Hardhat for Polygon Mumbai

Create `blockchain/hardhat.config.ts`:

```typescript
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    mumbai: {
      url: process.env.MUMBAI_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 80001
    }
  },
  etherscan: {
    apiKey: process.env.POLYGONSCAN_API_KEY
  }
};

export default config;
```

### 1.4 Set Up Environment Variables

Create `blockchain/.env`:

```bash
# Alchemy or Infura RPC URL
MUMBAI_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY

# Deployer wallet private key (testnet only!)
PRIVATE_KEY=your_testnet_private_key_here

# PolygonScan API key (for contract verification)
POLYGONSCAN_API_KEY=your_polygonscan_api_key
```

**⚠️ SECURITY NOTE:** Never commit `.env` files or use mainnet private keys!

### 1.5 Get Testnet MATIC

1. Visit Mumbai Faucet: https://faucet.polygon.technology/
2. Enter your wallet address
3. Receive 0.5 MATIC (enough for testing)
4. Verify balance:
   ```bash
   npx hardhat run scripts/checkBalance.ts --network mumbai
   ```

**Checkpoint:** ✅ Environment configured, testnet MATIC received

---

## Step 2: Smart Contract Development (Days 3-5)

### 2.1 VoteRegistry Contract

Create `blockchain/contracts/VoteRegistry.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title VoteRegistry
 * @dev Store cryptographic hashes of votes on blockchain
 */
contract VoteRegistry is Ownable, ReentrancyGuard, Pausable {

    struct Vote {
        bytes32 voteHash;           // Cryptographic hash of vote
        uint256 electionId;         // Election identifier
        uint256 timestamp;          // Block timestamp
        string referenceNumber;     // Unique reference for verification
        bool exists;                // Check if vote exists
    }

    // Mapping from reference number to vote
    mapping(string => Vote) public votes;

    // Mapping from election ID to vote count
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

    /**
     * @dev Record a vote on the blockchain
     * @param _voteHash Cryptographic hash of the vote
     * @param _electionId Election identifier
     * @param _referenceNumber Unique reference for this vote
     */
    function recordVote(
        bytes32 _voteHash,
        uint256 _electionId,
        string memory _referenceNumber
    ) external whenNotPaused nonReentrant {

        // Ensure vote doesn't already exist
        require(!votes[_referenceNumber].exists, "Vote already recorded");
        require(_voteHash != bytes32(0), "Invalid vote hash");
        require(bytes(_referenceNumber).length > 0, "Invalid reference number");

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
     * @dev Verify a vote exists and get its details
     * @param _referenceNumber The reference number to verify
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
     * @dev Get total number of votes recorded
     */
    function getTotalVotes() external view returns (uint256) {
        return allVotes.length;
    }

    /**
     * @dev Get vote by index (for enumeration)
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
     * @dev Emergency pause (only owner)
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause (only owner)
     */
    function unpause() external onlyOwner {
        _unpause();
    }
}
```

### 2.2 ElectionManager Contract

Create `blockchain/contracts/ElectionManager.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ElectionManager
 * @dev Manage election lifecycle on blockchain
 */
contract ElectionManager is Ownable {

    struct Election {
        uint256 id;
        string title;
        uint256 startTime;
        uint256 endTime;
        bool isActive;
        bool exists;
    }

    // Mapping from election ID to election
    mapping(uint256 => Election) public elections;

    // Array of all election IDs
    uint256[] public allElections;

    // Events
    event ElectionCreated(
        uint256 indexed electionId,
        string title,
        uint256 startTime,
        uint256 endTime
    );

    event ElectionActivated(uint256 indexed electionId);
    event ElectionDeactivated(uint256 indexed electionId);

    /**
     * @dev Create a new election
     */
    function createElection(
        uint256 _electionId,
        string memory _title,
        uint256 _startTime,
        uint256 _endTime
    ) external onlyOwner {
        require(!elections[_electionId].exists, "Election already exists");
        require(_endTime > _startTime, "End time must be after start time");
        require(_startTime > block.timestamp, "Start time must be in future");

        elections[_electionId] = Election({
            id: _electionId,
            title: _title,
            startTime: _startTime,
            endTime: _endTime,
            isActive: false,
            exists: true
        });

        allElections.push(_electionId);

        emit ElectionCreated(_electionId, _title, _startTime, _endTime);
    }

    /**
     * @dev Activate an election
     */
    function activateElection(uint256 _electionId) external onlyOwner {
        require(elections[_electionId].exists, "Election does not exist");
        require(!elections[_electionId].isActive, "Election already active");

        elections[_electionId].isActive = true;
        emit ElectionActivated(_electionId);
    }

    /**
     * @dev Deactivate an election
     */
    function deactivateElection(uint256 _electionId) external onlyOwner {
        require(elections[_electionId].exists, "Election does not exist");
        require(elections[_electionId].isActive, "Election not active");

        elections[_electionId].isActive = false;
        emit ElectionDeactivated(_electionId);
    }

    /**
     * @dev Check if election is currently ongoing
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
     * @dev Get total number of elections
     */
    function getTotalElections() external view returns (uint256) {
        return allElections.length;
    }
}
```

### 2.3 VoterRegistry Contract

Create `blockchain/contracts/VoterRegistry.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title VoterRegistry
 * @dev Track voter eligibility and voting status
 */
contract VoterRegistry is Ownable {

    // Mapping: voter address => election ID => has voted
    mapping(address => mapping(uint256 => bool)) public hasVoted;

    // Mapping: voter address => is eligible
    mapping(address => bool) public isEligible;

    // Events
    event VoterRegistered(address indexed voter);
    event VoterRemoved(address indexed voter);
    event VoteCast(address indexed voter, uint256 indexed electionId);

    /**
     * @dev Register a voter as eligible
     */
    function registerVoter(address _voter) external onlyOwner {
        require(_voter != address(0), "Invalid voter address");
        require(!isEligible[_voter], "Voter already registered");

        isEligible[_voter] = true;
        emit VoterRegistered(_voter);
    }

    /**
     * @dev Remove a voter's eligibility
     */
    function removeVoter(address _voter) external onlyOwner {
        require(isEligible[_voter], "Voter not registered");

        isEligible[_voter] = false;
        emit VoterRemoved(_voter);
    }

    /**
     * @dev Mark voter as having voted in an election
     */
    function markAsVoted(address _voter, uint256 _electionId) external onlyOwner {
        require(isEligible[_voter], "Voter not eligible");
        require(!hasVoted[_voter][_electionId], "Voter already voted");

        hasVoted[_voter][_electionId] = true;
        emit VoteCast(_voter, _electionId);
    }

    /**
     * @dev Check if voter has voted in an election
     */
    function checkHasVoted(address _voter, uint256 _electionId)
        external
        view
        returns (bool)
    {
        return hasVoted[_voter][_electionId];
    }

    /**
     * @dev Batch register multiple voters
     */
    function batchRegisterVoters(address[] memory _voters) external onlyOwner {
        for (uint256 i = 0; i < _voters.length; i++) {
            if (!isEligible[_voters[i]] && _voters[i] != address(0)) {
                isEligible[_voters[i]] = true;
                emit VoterRegistered(_voters[i]);
            }
        }
    }
}
```

### 2.4 Write Unit Tests

Create `blockchain/test/VoteRegistry.test.ts`:

```typescript
import { expect } from "chai";
import { ethers } from "hardhat";
import { VoteRegistry } from "../typechain-types";

describe("VoteRegistry", function () {
  let voteRegistry: VoteRegistry;
  let owner: any;
  let addr1: any;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    const VoteRegistry = await ethers.getContractFactory("VoteRegistry");
    voteRegistry = await VoteRegistry.deploy();
    await voteRegistry.deployed();
  });

  describe("Recording Votes", function () {
    it("Should record a vote successfully", async function () {
      const voteHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vote1"));
      const electionId = 1;
      const referenceNumber = "REF123";

      await expect(voteRegistry.recordVote(voteHash, electionId, referenceNumber))
        .to.emit(voteRegistry, "VoteRecorded")
        .withArgs(referenceNumber, voteHash, electionId, await getBlockTimestamp());

      const vote = await voteRegistry.verifyVote(referenceNumber);
      expect(vote.exists).to.be.true;
      expect(vote.voteHash).to.equal(voteHash);
      expect(vote.electionId).to.equal(electionId);
    });

    it("Should not allow duplicate votes", async function () {
      const voteHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vote1"));
      const referenceNumber = "REF123";

      await voteRegistry.recordVote(voteHash, 1, referenceNumber);

      await expect(
        voteRegistry.recordVote(voteHash, 1, referenceNumber)
      ).to.be.revertedWith("Vote already recorded");
    });

    it("Should increment election vote count", async function () {
      const voteHash1 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vote1"));
      const voteHash2 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vote2"));
      const electionId = 1;

      await voteRegistry.recordVote(voteHash1, electionId, "REF1");
      await voteRegistry.recordVote(voteHash2, electionId, "REF2");

      const count = await voteRegistry.electionVoteCount(electionId);
      expect(count).to.equal(2);
    });
  });

  describe("Vote Verification", function () {
    it("Should verify an existing vote", async function () {
      const voteHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vote1"));
      const referenceNumber = "REF123";

      await voteRegistry.recordVote(voteHash, 1, referenceNumber);

      const vote = await voteRegistry.verifyVote(referenceNumber);
      expect(vote.exists).to.be.true;
      expect(vote.voteHash).to.equal(voteHash);
    });

    it("Should return false for non-existent vote", async function () {
      const vote = await voteRegistry.verifyVote("NONEXISTENT");
      expect(vote.exists).to.be.false;
    });
  });

  describe("Enumeration", function () {
    it("Should track total votes correctly", async function () {
      await voteRegistry.recordVote(ethers.utils.keccak256(ethers.utils.toUtf8Bytes("v1")), 1, "R1");
      await voteRegistry.recordVote(ethers.utils.keccak256(ethers.utils.toUtf8Bytes("v2")), 1, "R2");
      await voteRegistry.recordVote(ethers.utils.keccak256(ethers.utils.toUtf8Bytes("v3")), 1, "R3");

      const total = await voteRegistry.getTotalVotes();
      expect(total).to.equal(3);
    });
  });

  describe("Pause Functionality", function () {
    it("Should not allow recording when paused", async function () {
      await voteRegistry.pause();

      await expect(
        voteRegistry.recordVote(ethers.utils.keccak256(ethers.utils.toUtf8Bytes("v1")), 1, "R1")
      ).to.be.revertedWith("Pausable: paused");
    });

    it("Should allow recording after unpause", async function () {
      await voteRegistry.pause();
      await voteRegistry.unpause();

      await expect(
        voteRegistry.recordVote(ethers.utils.keccak256(ethers.utils.toUtf8Bytes("v1")), 1, "R1")
      ).to.not.be.reverted;
    });
  });
});

async function getBlockTimestamp() {
  const blockNumber = await ethers.provider.getBlockNumber();
  const block = await ethers.provider.getBlock(blockNumber);
  return block.timestamp;
}
```

Run tests:

```bash
cd blockchain
npx hardhat test
```

**Expected output:** All tests passing ✅

**Checkpoint:** ✅ Smart contracts written and tested locally

---

## Step 3: Deploy to Mumbai Testnet (Days 6-7)

### 3.1 Create Deployment Script

Create `blockchain/scripts/deploy.ts`:

```typescript
import { ethers } from "hardhat";

async function main() {
  console.log("Starting deployment to Polygon Mumbai...");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy VoteRegistry
  console.log("\n1. Deploying VoteRegistry...");
  const VoteRegistry = await ethers.getContractFactory("VoteRegistry");
  const voteRegistry = await VoteRegistry.deploy();
  await voteRegistry.deployed();
  console.log("✅ VoteRegistry deployed to:", voteRegistry.address);

  // Deploy ElectionManager
  console.log("\n2. Deploying ElectionManager...");
  const ElectionManager = await ethers.getContractFactory("ElectionManager");
  const electionManager = await ElectionManager.deploy();
  await electionManager.deployed();
  console.log("✅ ElectionManager deployed to:", electionManager.address);

  // Deploy VoterRegistry
  console.log("\n3. Deploying VoterRegistry...");
  const VoterRegistry = await ethers.getContractFactory("VoterRegistry");
  const voterRegistry = await VoterRegistry.deploy();
  await voterRegistry.deployed();
  console.log("✅ VoterRegistry deployed to:", voterRegistry.address);

  // Save addresses
  const addresses = {
    voteRegistry: voteRegistry.address,
    electionManager: electionManager.address,
    voterRegistry: voterRegistry.address,
    network: "mumbai",
    deployer: deployer.address,
    timestamp: new Date().toISOString()
  };

  console.log("\n=== Deployment Summary ===");
  console.log(JSON.stringify(addresses, null, 2));

  // Save to file
  const fs = require("fs");
  fs.writeFileSync(
    "deployments/mumbai.json",
    JSON.stringify(addresses, null, 2)
  );
  console.log("\n✅ Addresses saved to deployments/mumbai.json");

  console.log("\n=== Verification Commands ===");
  console.log(`npx hardhat verify --network mumbai ${voteRegistry.address}`);
  console.log(`npx hardhat verify --network mumbai ${electionManager.address}`);
  console.log(`npx hardhat verify --network mumbai ${voterRegistry.address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### 3.2 Deploy

```bash
cd blockchain

# Create deployments directory
mkdir -p deployments

# Deploy to Mumbai
npx hardhat run scripts/deploy.ts --network mumbai
```

**Expected output:**
```
Starting deployment to Polygon Mumbai...
Deploying with account: 0x...
Account balance: 500000000000000000

1. Deploying VoteRegistry...
✅ VoteRegistry deployed to: 0xABC...

2. Deploying ElectionManager...
✅ ElectionManager deployed to: 0xDEF...

3. Deploying VoterRegistry...
✅ VoterRegistry deployed to: 0x123...

✅ Addresses saved to deployments/mumbai.json
```

### 3.3 Verify Contracts on PolygonScan

```bash
# Verify each contract
npx hardhat verify --network mumbai 0xYOUR_VOTE_REGISTRY_ADDRESS
npx hardhat verify --network mumbai 0xYOUR_ELECTION_MANAGER_ADDRESS
npx hardhat verify --network mumbai 0xYOUR_VOTER_REGISTRY_ADDRESS
```

Once verified, you can view your contracts at:
- https://mumbai.polygonscan.com/address/YOUR_CONTRACT_ADDRESS

**Checkpoint:** ✅ Contracts deployed to Mumbai and verified on PolygonScan

---

## Step 4: Python Backend Integration (Days 8-10)

### 4.1 Install Python Dependencies

```bash
cd /home/user/OVS

# Update requirements.txt
cat >> requirements.txt << EOF
web3==6.11.0
eth-account==0.10.0
python-dotenv==1.0.0
celery==5.3.4
redis==5.0.1
EOF

# Install
pip install -r requirements.txt
```

### 4.2 Create BlockchainService

Create `blockchain_service.py`:

```python
# blockchain_service.py
import json
import hashlib
from typing import Dict, Optional
from web3 import Web3
from eth_account import Account
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for interacting with blockchain smart contracts"""

    def __init__(self, config):
        """
        Initialize blockchain service

        Args:
            config: Flask config object with blockchain settings
        """
        self.w3 = Web3(Web3.HTTPProvider(config['MUMBAI_RPC_URL']))

        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to blockchain network")

        # Load contract ABIs and addresses
        with open('blockchain/deployments/mumbai.json', 'r') as f:
            self.addresses = json.load(f)

        # Load contract ABIs
        self.contracts = {
            'vote_registry': self._load_contract('VoteRegistry'),
            'election_manager': self._load_contract('ElectionManager'),
            'voter_registry': self._load_contract('VoterRegistry')
        }

        # Admin account for sending transactions
        self.admin_account = Account.from_key(config['BLOCKCHAIN_PRIVATE_KEY'])

        logger.info(f"Blockchain service initialized on network: {self.w3.eth.chain_id}")

    def _load_contract(self, contract_name: str):
        """Load contract ABI and create contract instance"""
        # Load ABI from artifacts
        abi_path = f'blockchain/artifacts/contracts/{contract_name}.sol/{contract_name}.json'
        with open(abi_path, 'r') as f:
            contract_json = json.load(f)
            abi = contract_json['abi']

        # Get address
        address_key = contract_name[0].lower() + contract_name[1:]  # camelCase
        address = self.addresses[address_key]

        # Create contract instance
        return self.w3.eth.contract(address=address, abi=abi)

    def record_vote(self, voter_id: str, candidate_id: int,
                    election_id: int, reference_number: str) -> Dict:
        """
        Record a vote on the blockchain

        Args:
            voter_id: Voter's ID
            candidate_id: Candidate's ID
            election_id: Election ID
            reference_number: Unique reference number

        Returns:
            Dict with transaction hash, block number, gas used
        """
        try:
            # Generate vote hash (anonymized)
            vote_hash = self._generate_vote_hash(
                voter_id, candidate_id, election_id, reference_number
            )

            # Build transaction
            contract = self.contracts['vote_registry']
            nonce = self.w3.eth.get_transaction_count(self.admin_account.address)

            # Estimate gas
            gas_estimate = contract.functions.recordVote(
                vote_hash,
                election_id,
                reference_number
            ).estimate_gas({'from': self.admin_account.address})

            # Build transaction
            tx = contract.functions.recordVote(
                vote_hash,
                election_id,
                reference_number
            ).build_transaction({
                'from': self.admin_account.address,
                'nonce': nonce,
                'gas': int(gas_estimate * 1.2),  # 20% buffer
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(
                tx, self.admin_account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt['status'] != 1:
                raise Exception("Transaction failed")

            logger.info(f"Vote recorded on blockchain: {tx_hash.hex()}")

            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'timestamp': datetime.utcnow(),
                'vote_hash': vote_hash.hex()
            }

        except Exception as e:
            logger.error(f"Failed to record vote on blockchain: {str(e)}")
            raise

    def verify_vote(self, reference_number: str) -> Dict:
        """
        Verify a vote exists on blockchain

        Args:
            reference_number: Reference number to verify

        Returns:
            Dict with vote details
        """
        try:
            contract = self.contracts['vote_registry']

            vote_data = contract.functions.verifyVote(reference_number).call()

            return {
                'exists': vote_data[3],
                'vote_hash': vote_data[0].hex(),
                'election_id': vote_data[1],
                'timestamp': datetime.fromtimestamp(vote_data[2]),
                'verified': True
            }

        except Exception as e:
            logger.error(f"Failed to verify vote: {str(e)}")
            return {'exists': False, 'verified': False}

    def get_election_vote_count(self, election_id: int) -> int:
        """Get total votes for an election from blockchain"""
        try:
            contract = self.contracts['vote_registry']
            count = contract.functions.electionVoteCount(election_id).call()
            return count
        except Exception as e:
            logger.error(f"Failed to get vote count: {str(e)}")
            return 0

    def get_blockchain_stats(self) -> Dict:
        """Get blockchain statistics for admin dashboard"""
        try:
            vote_contract = self.contracts['vote_registry']
            election_contract = self.contracts['election_manager']

            return {
                'connected': self.w3.is_connected(),
                'network': self.w3.eth.chain_id,
                'latest_block': self.w3.eth.block_number,
                'gas_price': self.w3.from_wei(self.w3.eth.gas_price, 'gwei'),
                'total_votes': vote_contract.functions.getTotalVotes().call(),
                'total_elections': election_contract.functions.getTotalElections().call(),
                'admin_balance': self.w3.from_wei(
                    self.w3.eth.get_balance(self.admin_account.address),
                    'ether'
                )
            }
        except Exception as e:
            logger.error(f"Failed to get blockchain stats: {str(e)}")
            return {'error': str(e)}

    def _generate_vote_hash(self, voter_id: str, candidate_id: int,
                           election_id: int, reference_number: str) -> bytes:
        """Generate anonymized vote hash"""
        data = f"{voter_id}:{candidate_id}:{election_id}:{reference_number}"
        return self.w3.keccak(text=data)

    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        return self.w3.is_connected()
```

### 4.3 Update Flask Configuration

Add to `config.py`:

```python
# Blockchain Configuration
MUMBAI_RPC_URL = os.environ.get('MUMBAI_RPC_URL', '')
BLOCKCHAIN_PRIVATE_KEY = os.environ.get('BLOCKCHAIN_PRIVATE_KEY', '')
BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'False').lower() == 'true'
```

Add to `.env`:

```bash
# Blockchain
BLOCKCHAIN_ENABLED=True
MUMBAI_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY
BLOCKCHAIN_PRIVATE_KEY=your_admin_private_key
```

### 4.4 Update Database Schema

Create migration: `migrations/add_blockchain_tables.sql`

```sql
-- blockchain_votes table
CREATE TABLE IF NOT EXISTS blockchain_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vote_id INTEGER NOT NULL,
    vote_hash VARCHAR(66) NOT NULL,
    transaction_hash VARCHAR(66) NOT NULL UNIQUE,
    block_number INTEGER NOT NULL,
    blockchain_timestamp DATETIME NOT NULL,
    gas_used INTEGER,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vote_id) REFERENCES votes(id)
);

CREATE INDEX idx_blockchain_votes_vote_id ON blockchain_votes(vote_id);
CREATE INDEX idx_blockchain_votes_tx_hash ON blockchain_votes(transaction_hash);
```

Run migration:

```bash
sqlite3 voting_system.db < migrations/add_blockchain_tables.sql
```

### 4.5 Update Models

Add to `models.py`:

```python
class BlockchainVote(db.Model):
    __tablename__ = 'blockchain_votes'

    id = db.Column(db.Integer, primary_key=True)
    vote_id = db.Column(db.Integer, db.ForeignKey('votes.id'), nullable=False)
    vote_hash = db.Column(db.String(66), nullable=False)
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False)
    block_number = db.Column(db.Integer, nullable=False)
    blockchain_timestamp = db.Column(db.DateTime, nullable=False)
    gas_used = db.Column(db.Integer)
    status = db.Column(db.String(20), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    vote = db.relationship('Vote', backref='blockchain_record', uselist=False)

    def __repr__(self):
        return f'<BlockchainVote {self.transaction_hash}>'
```

**Checkpoint:** ✅ Backend blockchain integration complete

---

## Step 5: Update Flask Routes (Days 11-12)

### 5.1 Update Vote Route

Modify `blueprints/main.py`:

```python
from blockchain_service import BlockchainService
from models import BlockchainVote

# Initialize blockchain service (add to app.py)
blockchain = None
if app.config['BLOCKCHAIN_ENABLED']:
    blockchain = BlockchainService(app.config)

@main_bp.route('/vote/<int:candidate_id>', methods=['GET', 'POST'])
@login_required
@verified_required
@not_voted_required
def vote(candidate_id):
    """Cast a vote (with blockchain recording)"""
    candidate = Candidate.query.get_or_404(candidate_id)
    election = Election.query.filter_by(is_active=True).first()

    if not election or not election.is_ongoing():
        flash('Voting is not currently open.', 'error')
        return redirect(url_for('main.dashboard'))

    form = VoteForm()
    if form.validate_on_submit():
        try:
            # Create reference number
            reference_number = generate_reference_number()

            # Create traditional vote record
            vote = Vote(
                voter_id=current_user.id,
                candidate_id=candidate_id,
                timestamp=datetime.utcnow(),
                reference_number=reference_number,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            db.session.add(vote)
            db.session.flush()  # Get vote.id

            # Record on blockchain (if enabled)
            if current_app.config['BLOCKCHAIN_ENABLED'] and blockchain:
                logger.info(f"Recording vote on blockchain for reference: {reference_number}")

                blockchain_result = blockchain.record_vote(
                    voter_id=current_user.voter_id,
                    candidate_id=candidate_id,
                    election_id=election.id,
                    reference_number=reference_number
                )

                # Store blockchain receipt
                blockchain_vote = BlockchainVote(
                    vote_id=vote.id,
                    vote_hash=blockchain_result['vote_hash'],
                    transaction_hash=blockchain_result['tx_hash'],
                    block_number=blockchain_result['block_number'],
                    blockchain_timestamp=blockchain_result['timestamp'],
                    gas_used=blockchain_result['gas_used'],
                    status='confirmed'
                )
                db.session.add(blockchain_vote)

                logger.info(f"Vote recorded on blockchain: {blockchain_result['tx_hash']}")

            # Update voter status
            current_user.has_voted = True
            db.session.commit()

            # Send confirmation
            send_vote_confirmation_email(current_user, vote)
            log_activity(current_user.id, 'VOTED', f'Voted for {candidate.name}')

            # Success message with blockchain info
            if current_app.config['BLOCKCHAIN_ENABLED']:
                flash(
                    f'Vote recorded successfully!<br>'
                    f'Reference: {reference_number}<br>'
                    f'Blockchain TX: <a href="https://mumbai.polygonscan.com/tx/{blockchain_result["tx_hash"]}" '
                    f'target="_blank">{blockchain_result["tx_hash"][:10]}...</a>',
                    'success'
                )
            else:
                flash(f'Thank you for voting! Reference: {reference_number}', 'success')

            return redirect(url_for('main.vote_confirmation',
                                   reference_number=reference_number))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Vote recording failed: {str(e)}")
            flash(f'Error recording vote: {str(e)}', 'error')
            return redirect(url_for('main.dashboard'))

    return render_template('vote.html', candidate=candidate, form=form)
```

### 5.2 Add Blockchain Verification Route

Add to `blueprints/main.py`:

```python
@main_bp.route('/verify-blockchain/<reference_number>')
def verify_blockchain(reference_number):
    """Verify vote on blockchain"""

    # Get vote from database
    vote = Vote.query.filter_by(reference_number=reference_number).first_or_404()
    blockchain_vote = BlockchainVote.query.filter_by(vote_id=vote.id).first()

    if not blockchain_vote:
        flash('This vote was not recorded on blockchain', 'warning')
        return redirect(url_for('main.verify_vote'))

    # Verify against blockchain
    if blockchain and current_app.config['BLOCKCHAIN_ENABLED']:
        chain_data = blockchain.verify_vote(reference_number)

        verification = {
            'local_data': {
                'reference': reference_number,
                'timestamp': vote.timestamp,
                'tx_hash': blockchain_vote.transaction_hash,
                'block_number': blockchain_vote.block_number
            },
            'blockchain_data': chain_data,
            'is_valid': chain_data['exists'] and chain_data['vote_hash'] == blockchain_vote.vote_hash,
            'explorer_url': f'https://mumbai.polygonscan.com/tx/{blockchain_vote.transaction_hash}'
        }

        return render_template('blockchain_verification.html',
                             verification=verification)
    else:
        flash('Blockchain verification not available', 'error')
        return redirect(url_for('main.verify_vote'))
```

**Checkpoint:** ✅ Vote recording with blockchain integration working

---

## Step 6: Admin Dashboard (Days 13-14)

### 6.1 Create Admin Blockchain Status Route

Add to `blueprints/admin.py`:

```python
@admin_bp.route('/blockchain-status')
@login_required
@admin_required
def blockchain_status():
    """Blockchain monitoring dashboard"""

    if not current_app.config['BLOCKCHAIN_ENABLED'] or not blockchain:
        flash('Blockchain integration is not enabled', 'warning')
        return redirect(url_for('admin.dashboard'))

    try:
        # Get blockchain stats
        stats = blockchain.get_blockchain_stats()

        # Get recent blockchain votes
        recent_votes = db.session.query(
            BlockchainVote, Vote
        ).join(Vote).order_by(
            BlockchainVote.created_at.desc()
        ).limit(10).all()

        # Calculate sync status
        local_vote_count = Vote.query.count()
        blockchain_vote_count = BlockchainVote.query.filter_by(status='confirmed').count()

        sync_status = {
            'local_votes': local_vote_count,
            'blockchain_votes': blockchain_vote_count,
            'unsynced': local_vote_count - blockchain_vote_count,
            'sync_percentage': (blockchain_vote_count / local_vote_count * 100) if local_vote_count > 0 else 0
        }

        return render_template('admin/blockchain_status.html',
                             stats=stats,
                             recent_votes=recent_votes,
                             sync_status=sync_status)

    except Exception as e:
        logger.error(f"Blockchain status error: {str(e)}")
        flash(f'Error loading blockchain status: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))
```

### 6.2 Create Template

Create `templates/admin/blockchain_status.html`:

```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h2>Blockchain Status</h2>

    <!-- Connection Status -->
    <div class="row mt-4">
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Connection</h5>
                    <p class="h3">
                        {% if stats.connected %}
                            <span class="badge bg-success">Connected</span>
                        {% else %}
                            <span class="badge bg-danger">Disconnected</span>
                        {% endif %}
                    </p>
                    <small>Network: {{ stats.network }}</small>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Total Votes</h5>
                    <p class="h3">{{ stats.total_votes }}</p>
                    <small>On blockchain</small>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Gas Price</h5>
                    <p class="h3">{{ "%.2f"|format(stats.gas_price) }}</p>
                    <small>Gwei</small>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Admin Balance</h5>
                    <p class="h3">{{ "%.4f"|format(stats.admin_balance) }}</p>
                    <small>MATIC</small>
                </div>
            </div>
        </div>
    </div>

    <!-- Sync Status -->
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>Synchronization Status</h5>
                </div>
                <div class="card-body">
                    <div class="progress" style="height: 30px;">
                        <div class="progress-bar" role="progressbar"
                             style="width: {{ sync_status.sync_percentage }}%"
                             aria-valuenow="{{ sync_status.sync_percentage }}"
                             aria-valuemin="0" aria-valuemax="100">
                            {{ "%.1f"|format(sync_status.sync_percentage) }}%
                        </div>
                    </div>
                    <div class="mt-2">
                        <strong>Local Votes:</strong> {{ sync_status.local_votes }} |
                        <strong>Blockchain Votes:</strong> {{ sync_status.blockchain_votes }} |
                        <strong>Unsynced:</strong> {{ sync_status.unsynced }}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Recent Votes -->
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>Recent Blockchain Votes</h5>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Reference</th>
                                <th>Transaction Hash</th>
                                <th>Block</th>
                                <th>Gas Used</th>
                                <th>Time</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for bc_vote, vote in recent_votes %}
                            <tr>
                                <td>{{ vote.reference_number[:10] }}...</td>
                                <td>
                                    <a href="https://mumbai.polygonscan.com/tx/{{ bc_vote.transaction_hash }}"
                                       target="_blank">
                                        {{ bc_vote.transaction_hash[:10] }}...
                                    </a>
                                </td>
                                <td>{{ bc_vote.block_number }}</td>
                                <td>{{ bc_vote.gas_used }}</td>
                                <td>{{ bc_vote.blockchain_timestamp.strftime('%Y-%m-%d %H:%M') }}</td>
                                <td>
                                    <a href="{{ url_for('main.verify_blockchain', reference_number=vote.reference_number) }}"
                                       class="btn btn-sm btn-primary">
                                        Verify
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Checkpoint:** ✅ Admin blockchain dashboard complete

---

## Step 7: Testing (Days 15-18)

### 7.1 Unit Testing

Create `tests/test_blockchain.py`:

```python
import pytest
from blockchain_service import BlockchainService
from app import create_app
from models import db, Vote, BlockchainVote, Voter, Candidate, Election
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def blockchain_service(app):
    return BlockchainService(app.config)

def test_blockchain_connection(blockchain_service):
    """Test blockchain connection"""
    assert blockchain_service.is_connected()

def test_vote_recording(app, blockchain_service):
    """Test recording vote on blockchain"""
    with app.app_context():
        # Create test data
        voter = Voter(name='Test', last_name='User', email='test@test.com',
                     voter_id='TEST001', is_verified=True)
        candidate = Candidate(name='Test Candidate', party='Test Party')
        election = Election(title='Test Election',
                          start_date=datetime.utcnow(),
                          end_date=datetime.utcnow() + timedelta(days=1))

        db.session.add_all([voter, candidate, election])
        db.session.commit()

        # Record vote
        result = blockchain_service.record_vote(
            voter_id=voter.voter_id,
            candidate_id=candidate.id,
            election_id=election.id,
            reference_number='TEST-REF-001'
        )

        assert result['success']
        assert 'tx_hash' in result
        assert result['block_number'] > 0

def test_vote_verification(blockchain_service):
    """Test vote verification"""
    # First record a vote
    result = blockchain_service.record_vote(
        voter_id='TEST001',
        candidate_id=1,
        election_id=1,
        reference_number='TEST-REF-002'
    )

    # Then verify it
    verification = blockchain_service.verify_vote('TEST-REF-002')

    assert verification['exists']
    assert verification['verified']
```

Run tests:

```bash
pytest tests/test_blockchain.py -v
```

### 7.2 Integration Testing

Test the full flow:

1. **Start Flask app**:
   ```bash
   python app.py
   ```

2. **Register a test voter**:
   - Go to http://localhost:5000/register
   - Fill in registration form
   - Admin approves voter

3. **Cast a vote**:
   - Login as voter
   - Select candidate
   - Cast vote
   - Note reference number and transaction hash

4. **Verify vote**:
   - Go to verification page
   - Enter reference number
   - Check blockchain verification link
   - Verify on PolygonScan

5. **Check admin dashboard**:
   - Login as admin
   - Go to blockchain status page
   - Verify vote appears in recent votes
   - Check gas used, block number

### 7.3 Load Testing

Create `tests/load_test.py`:

```python
from locust import HttpUser, task, between

class VotingUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def cast_vote(self):
        # Login
        self.client.post('/login', {
            'voter_id': 'TEST001',
            'password': 'Password123!'
        })

        # Cast vote
        response = self.client.post('/vote/1', {
            'confirm': True
        })

        assert response.status_code == 200
```

Run load test:

```bash
locust -f tests/load_test.py --headless -u 10 -r 1 -t 1m
```

**Checkpoint:** ✅ All tests passing

---

## Step 8: Documentation (Days 19-20)

### 8.1 Technical Documentation

Create `docs/BLOCKCHAIN_TECHNICAL_DOC.md`:
- Smart contract API
- BlockchainService API
- Database schema
- Deployment procedures
- Troubleshooting guide

### 8.2 User Documentation

Create `docs/USER_GUIDE_BLOCKCHAIN.md`:
- How blockchain verification works
- How to verify your vote
- Understanding transaction hashes
- FAQ

### 8.3 Runbook

Create `docs/BLOCKCHAIN_RUNBOOK.md`:
- Daily operations
- Monitoring procedures
- Incident response
- Common issues and solutions

**Checkpoint:** ✅ Documentation complete

---

## Deliverables Checklist

- [ ] Smart contracts deployed to Mumbai testnet
- [ ] Contract addresses documented
- [ ] Contracts verified on PolygonScan
- [ ] BlockchainService class implemented
- [ ] Database schema updated
- [ ] Flask routes updated for blockchain
- [ ] Admin blockchain dashboard created
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests successful
- [ ] Load testing completed
- [ ] Technical documentation complete
- [ ] User documentation complete
- [ ] Demo prepared
- [ ] Phase 1 review completed

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Test votes recorded | 100+ | ⬜ |
| Transaction success rate | >95% | ⬜ |
| Average gas cost per vote | <0.01 MATIC | ⬜ |
| Vote verification accuracy | 100% | ⬜ |
| All tests passing | Yes | ⬜ |
| Documentation complete | Yes | ⬜ |

---

## Common Issues & Solutions

### Issue: "Insufficient funds for gas"
**Solution:** Get more testnet MATIC from faucet

### Issue: "Transaction underpriced"
**Solution:** Increase gas price in transaction

### Issue: "Nonce too low"
**Solution:** Reset nonce or wait for pending transactions

### Issue: "Contract not deployed"
**Solution:** Check deployment addresses in mumbai.json

---

## Next Steps

Once Phase 1 is complete and all deliverables are met:

1. **Phase 1 Review**
   - Demo to stakeholders
   - Review metrics
   - Gather feedback
   - Document lessons learned

2. **Go/No-Go Decision**
   - Evaluate results against targets
   - Decide whether to proceed to Phase 2

3. **Phase 2 Preparation**
   - Identify pilot user group (50-200 voters)
   - Schedule pilot election
   - Brief support team

**[👉 Proceed to Phase 2: Pilot Election](./PHASE2_PILOT_ELECTION.md)**

---

**Document Status:** Ready for implementation
**Last Updated:** 2025-11-14
