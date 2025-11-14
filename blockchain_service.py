# blockchain_service.py
"""
Blockchain Service for OVS (Online Voting System)
Handles all interactions with Polygon blockchain smart contracts
"""

import json
import hashlib
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("⚠️  Warning: web3 not installed. Run: pip install web3 eth-account")
    Web3 = None
    Account = None

logger = logging.getLogger(__name__)


class BlockchainError(Exception):
    """Base exception for blockchain-related errors"""
    pass


class TransactionFailedError(BlockchainError):
    """Transaction reverted or failed"""
    pass


class NetworkError(BlockchainError):
    """Network connection issues"""
    pass


class BlockchainService:
    """
    Service for interacting with OVS smart contracts on Polygon blockchain

    Features:
    - Record votes on blockchain
    - Verify votes
    - Manage elections
    - Track voter eligibility
    """

    def __init__(self, config: Dict):
        """
        Initialize blockchain service

        Args:
            config: Flask config object or dict with:
                - MUMBAI_RPC_URL: RPC endpoint URL
                - BLOCKCHAIN_PRIVATE_KEY: Admin private key
                - BLOCKCHAIN_ENABLED: Whether blockchain is enabled
        """
        if not Web3:
            raise ImportError("web3 library not installed. Run: pip install web3 eth-account")

        self.enabled = config.get('BLOCKCHAIN_ENABLED', False)

        if not self.enabled:
            logger.info("Blockchain integration is disabled")
            return

        # Connect to Polygon
        rpc_url = config.get('MUMBAI_RPC_URL') or config.get('POLYGON_RPC_URL')
        if not rpc_url:
            raise BlockchainError("No RPC URL configured")

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not self.w3.is_connected():
            raise NetworkError(f"Failed to connect to blockchain at {rpc_url}")

        # Load contract addresses and ABIs
        self.contracts = self._load_contracts()

        # Admin account for sending transactions
        private_key = config.get('BLOCKCHAIN_PRIVATE_KEY')
        if private_key:
            self.admin_account = Account.from_key(private_key)
        else:
            logger.warning("No private key configured - read-only mode")
            self.admin_account = None

        logger.info(f"Blockchain service initialized on network: Chain ID {self.w3.eth.chain_id}")

    def _load_contracts(self) -> Dict:
        """Load contract ABIs and addresses"""
        # Determine deployment file based on chain ID
        chain_id = self.w3.eth.chain_id
        if chain_id == 80001:  # Mumbai testnet
            deployment_file = 'blockchain/deployments/mumbai.json'
        elif chain_id == 137:  # Polygon mainnet
            deployment_file = 'blockchain/deployments/polygon.json'
        else:
            raise BlockchainError(f"Unsupported chain ID: {chain_id}")

        deployment_path = Path(deployment_file)
        if not deployment_path.exists():
            raise BlockchainError(f"Deployment file not found: {deployment_file}")

        with open(deployment_path, 'r') as f:
            deployment = json.load(f)

        contracts = {}

        # Load VoteRegistry
        contracts['vote_registry'] = self._load_contract(
            'VoteRegistry',
            deployment['contracts']['VoteRegistry']['address']
        )

        # Load ElectionManager
        contracts['election_manager'] = self._load_contract(
            'ElectionManager',
            deployment['contracts']['ElectionManager']['address']
        )

        # Load VoterRegistry
        contracts['voter_registry'] = self._load_contract(
            'VoterRegistry',
            deployment['contracts']['VoterRegistry']['address']
        )

        return contracts

    def _load_contract(self, contract_name: str, address: str):
        """Load a single contract"""
        # Load ABI
        abi_path = Path(f'blockchain/artifacts/contracts/{contract_name}.sol/contracts_{contract_name}_sol_{contract_name}.abi')

        if not abi_path.exists():
            raise BlockchainError(f"ABI file not found: {abi_path}")

        with open(abi_path, 'r') as f:
            abi = json.load(f)

        # Create contract instance
        return self.w3.eth.contract(address=address, abi=abi)

    def generate_vote_hash(self, voter_id: str, candidate_id: int,
                          election_id: int, reference_number: str,
                          salt: str = "") -> bytes:
        """
        Generate cryptographic hash of vote for blockchain storage

        Args:
            voter_id: Voter's ID
            candidate_id: Candidate's ID
            election_id: Election ID
            reference_number: Unique reference
            salt: Optional salt for additional security

        Returns:
            32-byte hash as bytes
        """
        data = f"{voter_id}:{candidate_id}:{election_id}:{reference_number}:{salt}"
        return self.w3.keccak(text=data)

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
            Dict with transaction details:
                - success: bool
                - tx_hash: transaction hash
                - block_number: block number
                - gas_used: gas used
                - timestamp: timestamp
                - vote_hash: vote hash
        """
        if not self.enabled:
            raise BlockchainError("Blockchain is not enabled")

        if not self.admin_account:
            raise BlockchainError("No private key configured")

        try:
            # Generate vote hash
            vote_hash = self.generate_vote_hash(
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

            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.admin_account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt['status'] != 1:
                raise TransactionFailedError("Transaction reverted")

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
            raise BlockchainError(f"Vote recording failed: {str(e)}")

    def verify_vote(self, reference_number: str) -> Dict:
        """
        Verify a vote exists on blockchain

        Args:
            reference_number: Reference number to verify

        Returns:
            Dict with vote details:
                - exists: bool
                - vote_hash: vote hash
                - election_id: election ID
                - timestamp: timestamp
                - verified: bool
        """
        if not self.enabled:
            return {'exists': False, 'verified': False, 'error': 'Blockchain disabled'}

        try:
            contract = self.contracts['vote_registry']
            vote_data = contract.functions.verifyVote(reference_number).call()

            return {
                'exists': vote_data[3],
                'vote_hash': vote_data[0].hex() if vote_data[3] else None,
                'election_id': vote_data[1] if vote_data[3] else None,
                'timestamp': datetime.fromtimestamp(vote_data[2]) if vote_data[3] else None,
                'verified': vote_data[3]
            }

        except Exception as e:
            logger.error(f"Failed to verify vote: {str(e)}")
            return {'exists': False, 'verified': False, 'error': str(e)}

    def get_election_vote_count(self, election_id: int) -> int:
        """
        Get total votes for an election from blockchain

        Args:
            election_id: Election ID

        Returns:
            Vote count
        """
        if not self.enabled:
            return 0

        try:
            contract = self.contracts['vote_registry']
            count = contract.functions.electionVoteCount(election_id).call()
            return count
        except Exception as e:
            logger.error(f"Failed to get vote count: {str(e)}")
            return 0

    def get_total_votes(self) -> int:
        """Get total votes across all elections"""
        if not self.enabled:
            return 0

        try:
            contract = self.contracts['vote_registry']
            return contract.functions.getTotalVotes().call()
        except Exception as e:
            logger.error(f"Failed to get total votes: {str(e)}")
            return 0

    def get_blockchain_stats(self) -> Dict:
        """
        Get blockchain statistics for admin dashboard

        Returns:
            Dict with stats:
                - connected: bool
                - network: chain ID
                - latest_block: latest block number
                - gas_price: current gas price in Gwei
                - total_votes: total votes on chain
                - admin_balance: admin account balance
        """
        if not self.enabled:
            return {'error': 'Blockchain not enabled'}

        try:
            vote_contract = self.contracts['vote_registry']
            election_contract = self.contracts['election_manager']

            return {
                'connected': self.w3.is_connected(),
                'network': self.w3.eth.chain_id,
                'latest_block': self.w3.eth.block_number,
                'gas_price': float(self.w3.from_wei(self.w3.eth.gas_price, 'gwei')),
                'total_votes': vote_contract.functions.getTotalVotes().call(),
                'total_elections': election_contract.functions.getTotalElections().call(),
                'admin_balance': float(self.w3.from_wei(
                    self.w3.eth.get_balance(self.admin_account.address) if self.admin_account else 0,
                    'ether'
                )) if self.admin_account else None
            }
        except Exception as e:
            logger.error(f"Failed to get blockchain stats: {str(e)}")
            return {'error': str(e)}

    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        if not self.enabled:
            return False
        return self.w3.is_connected()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example configuration
    config = {
        'BLOCKCHAIN_ENABLED': True,
        'MUMBAI_RPC_URL': 'https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY',
        'BLOCKCHAIN_PRIVATE_KEY': 'your_private_key_here'
    }

    try:
        # Initialize service
        blockchain = BlockchainService(config)

        # Check connection
        if blockchain.is_connected():
            print("✅ Connected to blockchain")

            # Get stats
            stats = blockchain.get_blockchain_stats()
            print(f"📊 Stats: {stats}")
        else:
            print("❌ Not connected")

    except Exception as e:
        print(f"❌ Error: {e}")
