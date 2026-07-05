// 🌟 We use raw ethers to bypass Hardhat's internal environment matching rules
const { ethers } = require("ethers");

async function main() {
  console.log("Compiling and deploying EvidenceStore contract directly into Ganache...");

  // 1. Manually read the compiled contract blueprint data directly from your project artifacts
  const contractArtifact = require("../artifacts/contracts/EvidenceStore.sol/EvidenceStore.json");

  // 2. Point directly to your active Ganache desktop app port URL
  const provider = new ethers.JsonRpcProvider("http://127.0.0.1:7545");
  
  // 3. Grab the very first account sitting inside your Ganache window to sign the deployment block
  const signer = await provider.getSigner(0);

  // 4. Manually construct the Contract Factory using the contract's raw ABI layout and Bytecode bits
  const ContractFactory = new ethers.ContractFactory(
    contractArtifact.abi,
    contractArtifact.bytecode,
    signer
  );

  // 5. Send it across the wire to Ganache!
  const contractInstance = await ContractFactory.deploy();

  // 6. Wait a split second for Ganache to mine the block and finalize it
  await contractInstance.waitForDeployment();

  console.log(`\n=============================================================`);
  console.log(`✅ SUCCESS: Smart Contract deployed straight to Ganache!`);
  console.log(`📌 Copy this target address for your Python script:`);
  console.log(`${contractInstance.target}`);
  console.log(`=============================================================`);
}

main().catch((error) => {
  console.error("Deployment crashed with error details:", error);
  process.exitCode = 1;
});