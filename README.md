# Syrup
=====
[![License: GPL v3][license-badge]][license-badge-url]

Syrup runs Python3

## Installation (Ubuntu 20.04)

### 1. Install Solidity compiler (last version tested 0.8.1)

Download the folder ethir/source that contains static executables of
different versions of Solidity compiler.
    
Add it to the PATH and test that it is installed.
    
```
 sudo cp source/solc* /usr/bin/
 sudo chmod 755 /usr/bin/solc*
 solc --version
 solcv5 --version
 solcv6 --version
 solcv7 --version
 solcv8 --version
 ```
 
In case you want to install the latest version:
 
 ```
 sudo add-apt-repository ppa:ethereum/ethereum
 sudo apt-get update
 sudo apt-get install solc
```

### 2. Install Ethereum (last version tested 1.9.20)

A static executable is provided in the folder source.

Add ot to the PATh and test that it is installed.
 
 ```
 sudo cp source/evm* /usr/bin/
 sudo chmod 755 /usr/bin/evm*
 evm --version
 ```
 In case you want to install the latest version:
  
```
 sudo apt-get install software-properties-common
 sudo add-apt-repository -y ppa:ethereum/ethereum
 sudo apt-get update
 sudo apt-get install ethereum
```

### 3. Install [Z3]

Use `pip install` command to install Z3

```
pip3 install z3
pip3 install z3-solver
```
### 4. Install dependencies

Use `pip install` command to install six, requests python libraries.

```
pip install six
pip install requests
```

