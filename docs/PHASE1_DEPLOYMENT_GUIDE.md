# Phase 1: Blockchain Integration - Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-14
**Status:** Complete - Ready for Testing

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Smart Contract Deployment](#smart-contract-deployment)
4. [Database Migration](#database-migration)
5. [Application Configuration](#application-configuration)
6. [Testing the Integration](#testing-the-integration)
7. [Troubleshooting](#troubleshooting)
8. [Production Checklist](#production-checklist)

---

## Prerequisites

### Required Tools

- **Node.js** v16+ and npm (for smart contract compilation and deployment)
- **Python** 3.8+ with pip (backend application)
- **Git** (version control)
- **Polygon Mumbai** testnet wallet with MATIC tokens

### Required Accounts

1. **Alchemy or Infura Account** (for RPC access)
   - Sign up at https://alchemy.com or https://infura.io
   - Create a new app for Polygon Mumbai testnet
   - Copy your API key

2. **Polygon Mumbai Testnet Wallet**
   - Install MetaMask: https://metamask.io
   - Add Mumbai testnet network
   - Get test MATIC from faucet: https://faucet.polygon.technology/

3. **PolygonScan API Key** (optional, for contract verification)
   - Register at https://polygonscan.com
   - Go to API Keys and create new key

### Knowledge Prerequisites

- Basic understanding of blockchain and smart contracts
- Familiarity with Flask application deployment
- Command line experience
- Understanding of environment variables

---

## Environment Setup

### 1. Clone and Navigate to Project

```bash
cd /home/user/OVS
git pull origin main  # Get latest changes
```

### 2. Install Backend Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import web3; print(f'Web3.py version: {web3.__version__}')"
```

### 3. Install Blockchain Dependencies

```bash
cd blockchain

# Install Node.js dependencies
npm install

# Verify installation
npx hardhat --version
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:

```bash
# Blockchain Configuration
BLOCKCHAIN_ENABLED=True
BLOCKCHAIN_NETWORK=mumbai

# RPC URLs (replace YOUR_API_KEY with actual key)
MUMBAI_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Private key (from MetaMask - export private key)
# WARNING: Never commit this to Git!
BLOCKCHAIN_PRIVATE_KEY=your_private_key_without_0x_prefix

# Contract addresses (will be filled after deployment)
VOTE_REGISTRY_ADDRESS=
ELECTION_MANAGER_ADDRESS=
VOTER_REGISTRY_ADDRESS=

# Blockchain behavior
BLOCKCHAIN_ASYNC=False
BLOCKCHAIN_FAIL_GRACEFULLY=True
BLOCKCHAIN_BATCH_SIZE=50
```

**Security Note:** Never commit `.env` file to version control!

---

## Smart Contract Deployment

### Step 1: Compile Smart Contracts

```bash
cd /home/user/OVS/blockchain

# Compile contracts
npx hardhat compile

# Verify compilation success
ls -la artifacts/contracts/
```

You should see:
- `VoteRegistry.sol/VoteRegistry.json`
- `ElectionManager.sol/ElectionManager.json`
- `VoterRegistry.sol/VoterRegistry.json`

### Step 2: Deploy to Mumbai Testnet

```bash
# Deploy all contracts
npx hardhat run scripts/deploy.js --network mumbai
```

**Expected Output:**
```
Deploying contracts to Mumbai testnet...
Deployer: 0x1234...5678
Account balance: 1.5 MATIC

Deploying VoteRegistry...
VoteRegistry deployed to: 0xABC...DEF
Transaction hash: 0x123...789

Deploying ElectionManager...
ElectionManager deployed to: 0x456...ABC
Transaction hash: 0x789...012

Deploying VoterRegistry...
VoterRegistry deployed to: 0x789...XYZ
Transaction hash: 0x345...678

Deployment info saved to: deployments/mumbai.json
```

### Step 3: Verify Contracts on PolygonScan (Optional but Recommended)

```bash
# Verify VoteRegistry
npx hardhat verify --network mumbai <VOTE_REGISTRY_ADDRESS>

# Verify ElectionManager
npx hardhat verify --network mumbai <ELECTION_MANAGER_ADDRESS>

# Verify VoterRegistry
npx hardhat verify --network mumbai <VOTER_REGISTRY_ADDRESS>
```

### Step 4: Update Environment Variables

Open `deployments/mumbai.json` and copy contract addresses:

```json
{
  "network": "mumbai",
  "contracts": {
    "VoteRegistry": {
      "address": "0xABC...DEF",
      ...
    },
    "ElectionManager": {
      "address": "0x456...ABC",
      ...
    },
    "VoterRegistry": {
      "address": "0x789...XYZ",
      ...
    }
  }
}
```

Update your `.env` file:

```bash
VOTE_REGISTRY_ADDRESS=0xABC...DEF
ELECTION_MANAGER_ADDRESS=0x456...ABC
VOTER_REGISTRY_ADDRESS=0x789...XYZ
```

---

## Database Migration

### Step 1: Backup Existing Database

```bash
cd /home/user/OVS

# Backup SQLite database
cp voting_system.db voting_system_backup_$(date +%Y%m%d_%H%M%S).db

# Or for PostgreSQL
# pg_dump voting_system > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Run Migration

```bash
# Method 1: Using Flask shell
python << EOF
from app import app, db
from models import BlockchainVote, BlockchainElection, BlockchainTransaction, BlockchainSyncStatus

with app.app_context():
    db.create_all()
    print("Blockchain tables created successfully!")
EOF

# Method 2: Using raw SQL migration
sqlite3 voting_system.db < migrations/001_add_blockchain_tables.sql
```

### Step 3: Verify Migration

```bash
# Check if tables were created
python << EOF
from app import app, db
from models import BlockchainVote

with app.app_context():
    print(f"BlockchainVote table exists: {BlockchainVote.__table__.exists(db.engine)}")
EOF
```

---

## Application Configuration

### 1. Test Blockchain Connection

```bash
cd /home/user/OVS

# Test connection
python << EOF
from blockchain_service import BlockchainService

config = {
    'BLOCKCHAIN_NETWORK': 'mumbai',
    'MUMBAI_RPC_URL': 'YOUR_RPC_URL',
    'POLYGON_RPC_URL': '',
    'BLOCKCHAIN_PRIVATE_KEY': 'YOUR_PRIVATE_KEY',
    'VOTE_REGISTRY_ADDRESS': 'YOUR_VOTE_REGISTRY_ADDRESS',
    'ELECTION_MANAGER_ADDRESS': 'YOUR_ELECTION_MANAGER_ADDRESS',
    'VOTER_REGISTRY_ADDRESS': 'YOUR_VOTER_REGISTRY_ADDRESS'
}

service = BlockchainService(config)
status = service.get_connection_status()

print(f"Connected: {status['connected']}")
print(f"Network: {status.get('network')}")
print(f"Block: {status.get('latest_block')}")
print(f"Balance: {status.get('balance')} MATIC")
EOF
```

### 2. Initialize Blockchain Settings

```bash
# Start Flask application
python app.py

# Access admin blockchain dashboard
# Navigate to: http://localhost:5000/admin/blockchain
```

From the admin dashboard, you can:
- View connection status
- Test blockchain connectivity
- Monitor gas prices
- View transaction history

---

## Testing the Integration

### Test 1: Record a Test Vote on Blockchain

```bash
python << EOF
from app import app, db
from models import Voter, Candidate, Vote, Election, BlockchainVote
from blockchain_service import BlockchainService
from datetime import datetime, timedelta

with app.app_context():
    # Get active election
    election = Election.query.filter_by(is_active=True).first()
    if not election:
        # Create test election
        election = Election(
            title="Test Election 2025",
            description="Testing blockchain integration",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        db.session.add(election)
        db.session.commit()

    # Get test voter and candidate
    voter = Voter.query.first()
    candidate = Candidate.query.first()

    if voter and candidate:
        # Create vote
        vote = Vote(
            voter_id=voter.id,
            candidate_id=candidate.id,
            timestamp=datetime.utcnow(),
            reference_number=f"TEST-{datetime.utcnow().timestamp()}",
            ip_address="127.0.0.1"
        )
        db.session.add(vote)
        db.session.commit()

        # Record on blockchain
        from config import config
        blockchain_config = config['development']

        service = BlockchainService({
            'BLOCKCHAIN_NETWORK': blockchain_config.BLOCKCHAIN_NETWORK,
            'MUMBAI_RPC_URL': blockchain_config.MUMBAI_RPC_URL,
            'POLYGON_RPC_URL': blockchain_config.POLYGON_RPC_URL,
            'BLOCKCHAIN_PRIVATE_KEY': blockchain_config.BLOCKCHAIN_PRIVATE_KEY,
            'VOTE_REGISTRY_ADDRESS': blockchain_config.VOTE_REGISTRY_ADDRESS,
            'ELECTION_MANAGER_ADDRESS': blockchain_config.ELECTION_MANAGER_ADDRESS,
            'VOTER_REGISTRY_ADDRESS': blockchain_config.VOTER_REGISTRY_ADDRESS
        })

        result = service.record_vote(
            voter_id=voter.voter_id,
            candidate_id=candidate.id,
            election_id=election.id,
            reference_number=vote.reference_number
        )

        if result['success']:
            print(f"✅ Vote recorded on blockchain!")
            print(f"TX Hash: {result['tx_hash']}")
            print(f"Block: {result['block_number']}")
            print(f"Vote Hash: {result['vote_hash']}")
            print(f"Gas Used: {result.get('gas_used')}")

            # View on PolygonScan
            print(f"\nView transaction:")
            print(f"https://mumbai.polygonscan.com/tx/{result['tx_hash']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
EOF
```

### Test 2: Verify Vote on Blockchain

```bash
python << EOF
from blockchain_service import BlockchainService
from config import config

blockchain_config = config['development']

service = BlockchainService({
    'BLOCKCHAIN_NETWORK': blockchain_config.BLOCKCHAIN_NETWORK,
    'MUMBAI_RPC_URL': blockchain_config.MUMBAI_RPC_URL,
    'POLYGON_RPC_URL': blockchain_config.POLYGON_RPC_URL,
    'BLOCKCHAIN_PRIVATE_KEY': blockchain_config.BLOCKCHAIN_PRIVATE_KEY,
    'VOTE_REGISTRY_ADDRESS': blockchain_config.VOTE_REGISTRY_ADDRESS,
    'ELECTION_MANAGER_ADDRESS': blockchain_config.ELECTION_MANAGER_ADDRESS,
    'VOTER_REGISTRY_ADDRESS': blockchain_config.VOTER_REGISTRY_ADDRESS
})

# Use reference number from previous test
reference_number = "TEST-..."

verification = service.verify_vote(reference_number)

print(f"Vote exists: {verification['exists']}")
if verification['exists']:
    print(f"Vote hash: {verification['vote_hash']}")
    print(f"Election ID: {verification['election_id']}")
    print(f"Timestamp: {verification['timestamp']}")
EOF
```

### Test 3: End-to-End Web Application Test

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Login as admin:**
   - Navigate to http://localhost:5000/login
   - Use admin credentials from .env

3. **Access blockchain dashboard:**
   - Navigate to http://localhost:5000/admin/blockchain
   - Verify connection status is "Connected"
   - Check contract addresses are displayed

4. **Cast a test vote:**
   - Login as a regular voter
   - Navigate to dashboard
   - Vote for a candidate
   - Check for success message

5. **Verify blockchain recording:**
   - Go back to admin blockchain dashboard
   - Check "Total Blockchain Votes" increased
   - View recent transactions
   - Click transaction hash to view on PolygonScan

---

## Troubleshooting

### Issue 1: "Connection Error: Could not connect to RPC"

**Cause:** Invalid or expired RPC URL

**Solution:**
```bash
# Test RPC URL
curl -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  YOUR_MUMBAI_RPC_URL

# If this fails, generate new API key from Alchemy/Infura
```

### Issue 2: "Insufficient funds for gas"

**Cause:** Wallet has no MATIC tokens

**Solution:**
```bash
# Get free testnet MATIC
# Visit: https://faucet.polygon.technology/
# Enter your wallet address
# Wait 1-2 minutes for tokens to arrive

# Check balance
python << EOF
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('YOUR_MUMBAI_RPC_URL'))
account = '0xYOUR_WALLET_ADDRESS'
balance = w3.eth.get_balance(account)
print(f"Balance: {w3.from_wei(balance, 'ether')} MATIC")
EOF
```

### Issue 3: "Contract not deployed at address"

**Cause:** Wrong contract address or wrong network

**Solution:**
```bash
# Verify contract address on PolygonScan Mumbai
# https://mumbai.polygonscan.com/address/YOUR_CONTRACT_ADDRESS

# Re-deploy if necessary
cd blockchain
npx hardhat run scripts/deploy.js --network mumbai
```

### Issue 4: "BlockchainService not available"

**Cause:** Missing dependencies or import error

**Solution:**
```bash
# Reinstall dependencies
pip install web3==6.11.3 eth-account==0.10.0

# Test import
python -c "from blockchain_service import BlockchainService; print('✅ Import successful')"
```

### Issue 5: "Database migration failed"

**Cause:** Table already exists or syntax error

**Solution:**
```bash
# Drop blockchain tables and recreate
python << EOF
from app import app, db
with app.app_context():
    db.engine.execute("DROP TABLE IF EXISTS blockchain_votes")
    db.engine.execute("DROP TABLE IF EXISTS blockchain_elections")
    db.engine.execute("DROP TABLE IF EXISTS blockchain_transactions")
    db.engine.execute("DROP TABLE IF EXISTS blockchain_sync_status")
    db.create_all()
    print("✅ Tables recreated")
EOF
```

---

## Production Checklist

Before deploying to production (mainnet):

### Security

- [ ] Never commit `.env` file or private keys to Git
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS/SSL for application
- [ ] Implement rate limiting for blockchain operations
- [ ] Set up monitoring and alerts

### Testing

- [ ] Test all smart contract functions on Mumbai testnet
- [ ] Record at least 100+ test votes successfully
- [ ] Verify all votes on PolygonScan
- [ ] Test error handling (network failures, gas errors)
- [ ] Test admin dashboard functionality
- [ ] Load test the application

### Configuration

- [ ] Review gas price settings
- [ ] Set appropriate batch sizes
- [ ] Configure retry logic
- [ ] Enable async processing if needed
- [ ] Set up backup RPC providers

### Documentation

- [ ] Document deployment process
- [ ] Create runbooks for common operations
- [ ] Document troubleshooting procedures
- [ ] Train team on blockchain operations

### Mainnet Deployment

- [ ] Get professional security audit for smart contracts
- [ ] Deploy to Polygon mainnet
- [ ] Verify contracts on PolygonScan
- [ ] Fund production wallet with sufficient MATIC
- [ ] Update all contract addresses in production .env
- [ ] Test with small number of real votes first
- [ ] Monitor gas costs and optimize if needed

---

## Next Steps

After successful Phase 1 deployment:

1. **Monitor Performance:**
   - Track gas costs per vote
   - Monitor transaction success rate
   - Track average confirmation times

2. **Gather Feedback:**
   - User experience with blockchain verification
   - Admin experience with monitoring dashboard
   - Any issues or errors encountered

3. **Optimize:**
   - Implement batch voting if high volume
   - Add async processing with Celery
   - Optimize gas usage

4. **Prepare for Phase 2:**
   - Plan pilot election
   - Prepare communication materials
   - Train election officials

---

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review logs: `tail -f logs/app.log`
3. Check blockchain explorer: https://mumbai.polygonscan.com
4. Contact development team

---

## Resources

- **Polygon Mumbai Testnet:** https://mumbai.polygonscan.com
- **Mumbai Faucet:** https://faucet.polygon.technology/
- **Alchemy:** https://alchemy.com
- **Hardhat Documentation:** https://hardhat.org/docs
- **Web3.py Documentation:** https://web3py.readthedocs.io/
- **OpenZeppelin Contracts:** https://docs.openzeppelin.com/contracts/

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-14
**Next Review:** After Phase 1 testing complete
