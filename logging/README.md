# 🐍 Python Class & Method Reference: `testRFL.py`

This document describes the main classes and methods in the `testRFL.py` file for the RL-based threat detection system in a banking application.

---

## Classes & Methods

### 1. `BankingEnvironment`
Simulates the banking environment for RL training and evaluation.

- **`__init__()`**  
  Initializes environment state, threat types, and legitimate transaction patterns.
- **`reset()`**  
  Resets the environment for a new episode.
- **`_generate_legitimate_patterns()`**  
  Returns typical patterns for legitimate transactions.
- **`generate_transaction(is_threat=False, threat_type=None)`**  
  Generates a transaction (legitimate or threat) with features.
- **`_add_threat_indicators(threat_type)`**  
  Adds threat-specific indicators to a transaction.
- **`step(action, transaction)`**  
  Simulates taking an action (allow, flag, block) and returns reward, new state, and info.
- **`_get_state()`**  
  Returns current environment metrics (step, detection rate, etc.).
- **`_get_info()`**  
  Returns additional info (accuracy, customer impact).

---

### 2. `ThreatDetectionAgent`
Implements a Q-learning agent for threat detection.

- **`__init__(learning_rate, discount_factor, epsilon)`**  
  Sets learning parameters and initializes the Q-table.
- **`get_state_key(transaction, env_state)`**  
  Encodes transaction and environment state into a tuple for Q-table lookup.
- **`choose_action(state_key)`**  
  Selects an action using epsilon-greedy policy.
- **`update_q_value(state_key, action, reward, next_state_key)`**  
  Updates the Q-table using the Q-learning update rule.
- **`decay_epsilon(decay_rate)`**  
  Decays the exploration rate over time.

---

### 3. `FeatureEncoder`
Encodes transaction features for the RL agent.

- **`encode(transaction)`**  
  Converts transaction features into a normalized numerical vector.

---

### 4. `ThreatDetectionSystem`
Orchestrates the environment and agent, manages training, and provides threat prediction.

- **`__init__()`**  
  Initializes the environment, agent, and training history.
- **`train(episodes=1000)`**  
  Trains the RL agent for a specified number of episodes.
- **`predict_threat(transaction_data)`**  
  Predicts if a transaction is a threat and returns action, confidence, and risk score.
- **`_format_transaction(transaction_data)`**  
  Formats input transaction data for prediction.
- **`_analyze_threat_indicators(transaction)`**  
  Extracts and lists active threat indicators from a transaction.
- **`get_training_summary()`**  
  Summarizes training performance (reward, detection rate, etc.).

---

### 5. `demo_threat_detection()`
Demonstrates the system by training the agent and testing it on sample transactions.

- Initializes the system and trains it.
- Prints training summary.
- Tests the trained agent on example transactions and prints the results.

---

**Usage:**  
Run the script to train and test the RL-based threat detection system for banking transactions.