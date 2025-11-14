// Deploy script for OVS Blockchain Contracts
// Usage: npx hardhat run scripts/deploy.js --network mumbai

const fs = require('fs');
const path = require('path');

async function main() {
  console.log("🚀 Starting OVS Blockchain Deployment...\n");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying contracts with account:", deployer.address);

  const balance = await deployer.getBalance();
  console.log("💰 Account balance:", ethers.utils.formatEther(balance), "MATIC\n");

  if (balance.lt(ethers.utils.parseEther("0.1"))) {
    console.warn("⚠️  Warning: Low balance. You may need more MATIC for deployment.");
    console.warn("   Get testnet MATIC from: https://faucet.polygon.technology/\n");
  }

  // Load compiled contract artifacts
  const voteRegistryArtifact = JSON.parse(
    fs.readFileSync('artifacts/contracts/VoteRegistry.sol/contracts_VoteRegistry_sol_VoteRegistry.abi', 'utf8')
  );
  const electionManagerArtifact = JSON.parse(
    fs.readFileSync('artifacts/contracts/ElectionManager.sol/contracts_ElectionManager_sol_ElectionManager.abi', 'utf8')
  );
  const voterRegistryArtifact = JSON.parse(
    fs.readFileSync('artifacts/contracts/VoterRegistry.sol/contracts_VoterRegistry_sol_VoterRegistry.abi', 'utf8')
  );

  // Deploy VoteRegistry
  console.log("1️⃣  Deploying VoteRegistry...");
  const VoteRegistry = await ethers.getContractFactory("VoteRegistry", {
    abi: voteRegistryArtifact
  });
  const voteRegistry = await VoteRegistry.deploy();
  await voteRegistry.deployed();
  console.log("   ✅ VoteRegistry deployed to:", voteRegistry.address);
  console.log("   ⏳ Waiting for confirmations...");
  await voteRegistry.deployTransaction.wait(3);
  console.log("   ✅ Confirmed!\n");

  // Deploy ElectionManager
  console.log("2️⃣  Deploying ElectionManager...");
  const ElectionManager = await ethers.getContractFactory("ElectionManager", {
    abi: electionManagerArtifact
  });
  const electionManager = await ElectionManager.deploy();
  await electionManager.deployed();
  console.log("   ✅ ElectionManager deployed to:", electionManager.address);
  console.log("   ⏳ Waiting for confirmations...");
  await electionManager.deployTransaction.wait(3);
  console.log("   ✅ Confirmed!\n");

  // Deploy VoterRegistry
  console.log("3️⃣  Deploying VoterRegistry...");
  const VoterRegistry = await ethers.getContractFactory("VoterRegistry", {
    abi: voterRegistryArtifact
  });
  const voterRegistry = await VoterRegistry.deploy();
  await voterRegistry.deployed();
  console.log("   ✅ VoterRegistry deployed to:", voterRegistry.address);
  console.log("   ⏳ Waiting for confirmations...");
  await voterRegistry.deployTransaction.wait(3);
  console.log("   ✅ Confirmed!\n");

  // Calculate deployment costs
  const voteRegistryReceipt = await voteRegistry.deployTransaction.wait();
  const electionManagerReceipt = await electionManager.deployTransaction.wait();
  const voterRegistryReceipt = await voterRegistry.deployTransaction.wait();

  const totalGasUsed = voteRegistryReceipt.gasUsed
    .add(electionManagerReceipt.gasUsed)
    .add(voterRegistryReceipt.gasUsed);

  const gasPrice = voteRegistry.deployTransaction.gasPrice;
  const totalCost = totalGasUsed.mul(gasPrice);

  // Prepare deployment info
  const network = await ethers.provider.getNetwork();
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      VoteRegistry: {
        address: voteRegistry.address,
        transactionHash: voteRegistry.deployTransaction.hash,
        blockNumber: voteRegistryReceipt.blockNumber,
        gasUsed: voteRegistryReceipt.gasUsed.toString()
      },
      ElectionManager: {
        address: electionManager.address,
        transactionHash: electionManager.deployTransaction.hash,
        blockNumber: electionManagerReceipt.blockNumber,
        gasUsed: electionManagerReceipt.gasUsed.toString()
      },
      VoterRegistry: {
        address: voterRegistry.address,
        transactionHash: voterRegistry.deployTransaction.hash,
        blockNumber: voterRegistryReceipt.blockNumber,
        gasUsed: voterRegistryReceipt.gasUsed.toString()
      }
    },
    deployment: {
      totalGasUsed: totalGasUsed.toString(),
      gasPriceGwei: ethers.utils.formatUnits(gasPrice, "gwei"),
      totalCostMATIC: ethers.utils.formatEther(totalCost),
      totalCostUSD: `~$${(parseFloat(ethers.utils.formatEther(totalCost)) * 0.65).toFixed(2)}`
    }
  };

  // Save deployment info
  const deploymentsDir = path.join(__dirname, '..', 'deployments');
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const filename = network.name === 'mumbai' ? 'mumbai.json' : 'polygon.json';
  const filepath = path.join(deploymentsDir, filename);

  fs.writeFileSync(filepath, JSON.stringify(deploymentInfo, null, 2));

  // Print summary
  console.log("=" .repeat(60));
  console.log("📊 DEPLOYMENT SUMMARY");
  console.log("=".repeat(60));
  console.log(`Network:           ${network.name} (Chain ID: ${network.chainId})`);
  console.log(`Deployer:          ${deployer.address}`);
  console.log(`\nContracts:`);
  console.log(`  VoteRegistry:    ${voteRegistry.address}`);
  console.log(`  ElectionManager: ${electionManager.address}`);
  console.log(`  VoterRegistry:   ${voterRegistry.address}`);
  console.log(`\nCosts:`);
  console.log(`  Total Gas Used:  ${totalGasUsed.toString()}`);
  console.log(`  Gas Price:       ${ethers.utils.formatUnits(gasPrice, "gwei")} Gwei`);
  console.log(`  Total Cost:      ${ethers.utils.formatEther(totalCost)} MATIC`);
  console.log(`  Estimated USD:   ${deploymentInfo.deployment.totalCostUSD}`);
  console.log("=".repeat(60));

  console.log(`\n✅ Deployment info saved to: ${filepath}`);

  console.log("\n🔍 NEXT STEPS:");
  console.log("1. Verify contracts on PolygonScan:");
  console.log(`   npx hardhat verify --network ${network.name} ${voteRegistry.address}`);
  console.log(`   npx hardhat verify --network ${network.name} ${electionManager.address}`);
  console.log(`   npx hardhat verify --network ${network.name} ${voterRegistry.address}`);
  console.log("\n2. View on PolygonScan:");
  if (network.name === 'mumbai') {
    console.log(`   https://mumbai.polygonscan.com/address/${voteRegistry.address}`);
  } else {
    console.log(`   https://polygonscan.com/address/${voteRegistry.address}`);
  }
  console.log("\n3. Update Python backend with contract addresses from:");
  console.log(`   ${filepath}`);

  console.log("\n🎉 Deployment complete!\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });
