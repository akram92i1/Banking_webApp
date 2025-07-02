import numpy as np
import pandas as pd
import random
from collections import deque, defaultdict
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Any
import warnings
from colorama import Fore, Style
import matplotlib.pyplot as plt
import pickle 
from collections import defaultdict
warnings.filterwarnings('ignore')

class BankingEnvironment:
    """Banking environment for RL threat detection"""
    
    def __init__(self):
        self.reset()
        self.threat_types = [
            'account_takeover', 'card_fraud', 'phishing', 
            'money_laundering', 'identity_theft', 'insider_threat'
        ]
        self.legitimate_patterns = self._generate_legitimate_patterns()
        
    def reset(self):
        """Reset environment state"""
        self.current_step = 0
        self.detected_threats = 0
        self.false_positives = 0
        self.missed_threats = 0
        self.customer_satisfaction = 100.0
        return self._get_state()
    
    def _generate_legitimate_patterns(self):
        """Generate typical legitimate banking patterns"""
        return {
            'normal_transaction_times': list(range(8, 22)),  # 8AM-10PM
            'typical_amounts': [10, 25, 50, 100, 200, 500],
            'common_merchants': ['grocery', 'gas', 'restaurant', 'retail', 'utility'],
            'usual_locations': ['home_city', 'work_area', 'shopping_district']
        }
    
    def generate_transaction(self, is_threat=False, threat_type=None):
        """Generate a banking transaction (legitimate or threat)"""
        base_features = {
            'timestamp': datetime.now() - timedelta(minutes=random.randint(0, 1440)),
            'amount': random.choice([10, 25, 50, 100, 200, 500, 1000, 2000]),
            'merchant_type': random.choice(['grocery', 'gas', 'restaurant', 'retail', 'atm', 'online']),
            'location': random.choice(['home', 'work', 'mall', 'unknown', 'foreign']),
            'device_id': f"device_{random.randint(1, 100)}",
            'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
        }
        
        if is_threat and threat_type:
            base_features.update(self._add_threat_indicators(threat_type))
            base_features['is_threat'] = True
            base_features['threat_type'] = threat_type
        else:
            base_features['is_threat'] = False
            base_features['threat_type'] = None
            
        return base_features
    
    def _add_threat_indicators(self, threat_type):
        """Add threat-specific indicators to transaction"""
        indicators = {}
        
        if threat_type == 'account_takeover':
            indicators.update({
                'unusual_device': True,
                'location_mismatch': True,
                'rapid_transactions': True,
                'amount': random.choice([5000, 10000, 15000])
            })
        elif threat_type == 'card_fraud':
            indicators.update({
                'location': 'foreign',
                'unusual_merchant': True,
                'amount': random.choice([2000, 5000, 8000])
            })
        elif threat_type == 'phishing':
            indicators.update({
                'suspicious_ip': True,
                'login_attempts': random.randint(5, 15),
                'credential_stuffing': True
            })
        elif threat_type == 'money_laundering':
            indicators.update({
                'round_amounts': True,
                'rapid_transfers': True,
                'amount': random.choice([9000, 9500, 9900])  # Just under reporting thresholds
            })
        elif threat_type == 'identity_theft':
            indicators.update({
                'new_payee': True,
                'personal_info_change': True,
                'urgent_transfer': True
            })
        elif threat_type == 'insider_threat':
            indicators.update({
                'admin_access': True,
                'bulk_data_access': True,
                'after_hours': True
            })
            
        return indicators
    
    def step(self, action, transaction):
        """Execute action in environment and return reward"""
        # action: 0 = allow, 1 = flag as suspicious, 2 = block
        is_actual_threat = transaction['is_threat']
        reward = 0
        
        if action == 0:  # Allow transaction
            if is_actual_threat:
                # Missed a threat - significant penalty
                reward = -100
                self.missed_threats += 1
            else:
                # Correctly allowed legitimate transaction
                reward = 10
        
        elif action == 1:  # Flag as suspicious
            if is_actual_threat:
                # Correctly flagged threat
                reward = 50
                self.detected_threats += 1
            else:
                # False positive - minor penalty
                reward = -20
                self.false_positives += 1
                self.customer_satisfaction -= 2
        
        elif action == 2:  # Block transaction
            if is_actual_threat:
                # Correctly blocked threat - highest reward
                reward = 100
                self.detected_threats += 1
            else:
                # Blocked legitimate transaction - major penalty
                reward = -50
                self.false_positives += 1
                self.customer_satisfaction -= 5
        
        self.current_step += 1
        done = self.current_step >= 1000  # Episode length
        
        return self._get_state(), reward, done, self._get_info()
    
    def _get_state(self):
        """Get current environment state"""
        return {
            'step': self.current_step,
            'detected_threats': self.detected_threats,
            'false_positives': self.false_positives,
            'missed_threats': self.missed_threats,
            'customer_satisfaction': self.customer_satisfaction,
            'detection_rate': self.detected_threats / max(1, self.detected_threats + self.missed_threats),
            'false_positive_rate': self.false_positives / max(1, self.current_step)
        }
    
    def _get_info(self):
        """Get additional information"""
        return {
            'total_transactions': self.current_step,
            'threat_detection_accuracy': self.detected_threats / max(1, self.detected_threats + self.missed_threats),
            'customer_impact': 100 - self.customer_satisfaction
        }

class ThreatDetectionAgent:
    """Q-Learning agent for threat detection"""
    def float_defaultdict(self):
        """Default dictionary for float values"""
        return defaultdict(float)   
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.q_table = defaultdict(self.float_defaultdict)
        self.feature_encoder = FeatureEncoder()
        
    def get_state_key(self, transaction, env_state):
        """Convert transaction and environment state to state key"""
        features = self.feature_encoder.encode(transaction)
        env_features = [
            env_state['detection_rate'],
            env_state['false_positive_rate'],
            env_state['customer_satisfaction'] / 100.0
        ]
        
        # Discretize continuous features
        state_key = tuple([
            int(features[0] * 10),  # Amount bucket
            int(features[1]),       # Time bucket
            int(features[2]),       # Location bucket
            int(features[3]),       # Device bucket
            int(env_features[0] * 10),  # Detection rate bucket
            int(env_features[1] * 10),  # FP rate bucket
            int(env_features[2] * 10)   # Customer satisfaction bucket
        ])
        
        return state_key
    
    def choose_action(self, state_key):
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            return random.randint(0, 2)  # Random action
        else:
            q_values = self.q_table[state_key]
            if not q_values:
                return random.randint(0, 2)
            return max(q_values, key=q_values.get)
    
    def choose_action_boltzmann(self, state_key, temperature=1.0):
        """Choose action using Boltzmann exploration"""
        q_values = self.q_table[state_key]
        actions = [0, 1, 2]
        if not q_values:
            return random.choice(actions)
        # Get Q-values for all actions, defaulting to 0.0 if missing
        q_list = np.array([q_values.get(a, 0.0) for a in actions])
        # Prevent division by zero or overflow
        temp = max(temperature, 1e-6)
        exp_q = np.exp(q_list / temp)
        sum_exp_q = np.sum(exp_q)
        if sum_exp_q == 0 or np.isnan(sum_exp_q):
            # All Q-values are zero or invalid, pick random action
            return random.choice(actions)
        probabilities = exp_q / sum_exp_q
        # print(Fore.BLUE, f"Action probabilities for state {state_key}: {probabilities}", Style.RESET_ALL)
        if np.any(np.isnan(probabilities)):
            return random.choice(actions)
        return np.random.choice(actions, p=probabilities)
    def update_q_value(self, state_key, action, reward, next_state_key):
        """Update Q-value using Q-learning update rule"""
        current_q = self.q_table[state_key][action]
        next_max_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
        
        new_q = current_q + self.lr * (reward + self.gamma * next_max_q - current_q)
        self.q_table[state_key][action] = new_q
    
    def decay_epsilon(self, decay_rate=0.995):
        """Decay exploration rate"""
        self.epsilon = max(0.01, self.epsilon * decay_rate)

class FeatureEncoder:
    """Encode transaction features for RL agent"""
    
    def encode(self, transaction):
        """Encode transaction into numerical features"""
        features = []
        
        # Amount feature (normalized)
        amount = transaction.get('amount', 0)
        features.append(min(amount / 10000.0, 1.0))  # Normalize to [0,1]
        
        # Time feature (hour of day)
        timestamp = transaction.get('timestamp', datetime.now())
        features.append(timestamp.hour / 24.0)
        
        # Location risk score
        location = transaction.get('location', 'unknown')
        location_risk = {
            'home': 0.1, 'work': 0.2, 'mall': 0.3, 
            'unknown': 0.7, 'foreign': 0.9
        }
        features.append(location_risk.get(location, 0.5))
        
        # Device risk score
        device_known = not transaction.get('unusual_device', False)
        features.append(0.1 if device_known else 0.8)
        
        # Velocity features
        features.append(1.0 if transaction.get('rapid_transactions', False) else 0.1)
        features.append(1.0 if transaction.get('rapid_transfers', False) else 0.1)
        
        # Behavioral anomalies
        features.append(1.0 if transaction.get('location_mismatch', False) else 0.1)
        features.append(1.0 if transaction.get('suspicious_ip', False) else 0.1)
        
        return features

class ThreatDetectionSystem:
    """Main threat detection system"""
    
    def __init__(self):
        self.environment = BankingEnvironment()
        self.agent = ThreatDetectionAgent()
        self.training_history = []
        self.threat_patterns = {}
        
    def train(self, episodes=10000):
        """Train the RL agent"""
        print("Starting training...")
        
        for episode in range(episodes):
            state = self.environment.reset()
            total_reward = 0
            threats_in_episode = 0
            
            for step in range(50000):  # Steps per episode
                # Generate transaction (20% chance of threat)
                is_threat = random.random() < 0.2
                # print(Fore.YELLOW, f"Generating transaction for Episode {episode}, Step {step}...", Style.RESET_ALL)
                # Randomly select threat type if it's a threat
                threat_type = random.choice(self.environment.threat_types) if is_threat else None
                # print(Fore.GREEN,f"Episode {episode}, Step {step}: {'Threat' if is_threat else 'Legitimate'} transaction", Style.RESET_ALL)
                transaction = self.environment.generate_transaction(is_threat, threat_type)
                if is_threat:
                    threats_in_episode += 1
                
                # Get state representation
                state_key = self.agent.get_state_key(transaction, state)
                
                # Choose action
                action = self.agent.choose_action_boltzmann(state_key)
                
                # Execute action
                next_state, reward, done, info = self.environment.step(action, transaction)
                next_state_key = self.agent.get_state_key(transaction, next_state)
                
                # Update Q-value
                self.agent.update_q_value(state_key, action, reward, next_state_key)
                
                total_reward += reward
                state = next_state
                
                if done:
                    break
            
            # Decay exploration
            self.agent.decay_epsilon()
            
            # Record training progress
            self.training_history.append({
                'episode': episode,
                'total_reward': total_reward,
                'threats_detected': self.environment.detected_threats,
                'false_positives': self.environment.false_positives,
                'missed_threats': self.environment.missed_threats,
                'detection_rate': info.get('threat_detection_accuracy', 0),
                'customer_satisfaction': self.environment.customer_satisfaction
            })
            
            if episode % 100 == 0:
                print(f"Episode {episode}: Reward={total_reward:.2f}, "
                      f"Detection Rate={info.get('threat_detection_accuracy', 0):.3f}, "
                      f"Customer Satisfaction={self.environment.customer_satisfaction:.1f}")
    
    def predict_threat(self, transaction_data):
        """Predict if a transaction is a threat"""
        # Convert transaction data to proper format
        transaction = self._format_transaction(transaction_data)
        
        # Get current environment state (in production, this would be real-time metrics)
        # This will be connected to a live system in a real application via containers or APIs 
        env_state = {
            'detection_rate': 0.85,
            'false_positive_rate': 0.05,
            'customer_satisfaction': 95.0
        }
        
        # Get state representation
        state_key = self.agent.get_state_key(transaction, env_state)
        
        # Get action probabilities
        q_values = self.agent.q_table[state_key]
        if not q_values:
            return {'action': 'allow', 'confidence': 0.5, 'risk_score': 0.5, 'threat_indicators': self._analyze_threat_indicators(transaction)}
        
        best_action = max(q_values, key=q_values.get)
        max_q_value = max(q_values.values())
        min_q_value = min(q_values.values())
        
        # Normalize confidence
        confidence = (max_q_value - min_q_value) / max(1, abs(max_q_value) + abs(min_q_value))
        
        action_names = {0: 'allow', 1: 'flag', 2: 'block'}
        
        # Calculate risk score based on transaction features
        features = self.agent.feature_encoder.encode(transaction)
        risk_score = np.mean(features)
        
        return {
            'action': action_names[best_action],
            'confidence': confidence,
            'risk_score': risk_score,
            'q_values': dict(q_values),
            'threat_indicators': self._analyze_threat_indicators(transaction)
        }
    
    def _format_transaction(self, transaction_data):
        """Format input transaction data"""
        # Ensure required fields exist
        formatted = {
            'timestamp': transaction_data.get('timestamp', datetime.now()),
            'amount': transaction_data.get('amount', 0),
            'merchant_type': transaction_data.get('merchant_type', 'unknown'),
            'location': transaction_data.get('location', 'unknown'),
            'device_id': transaction_data.get('device_id', 'unknown'),
            'ip_address': transaction_data.get('ip_address', 'unknown'),
        }
        
        # Add any threat indicators that might be present
        threat_indicators = [
            'unusual_device', 'location_mismatch', 'rapid_transactions',
            'suspicious_ip', 'login_attempts', 'credential_stuffing',
            'round_amounts', 'rapid_transfers', 'new_payee',
            'personal_info_change', 'urgent_transfer', 'admin_access',
            'bulk_data_access', 'after_hours'
        ]
        
        for indicator in threat_indicators:
            if indicator in transaction_data:
                formatted[indicator] = transaction_data[indicator]
        
        return formatted
    
    def _analyze_threat_indicators(self, transaction):
        """Analyze and return active threat indicators"""
        indicators = []
        
        # Check for various threat patterns
        if transaction.get('amount', 0) > 5000:
            indicators.append('high_amount')
        
        if transaction.get('location') == 'foreign':
            indicators.append('foreign_location')
        
        if transaction.get('unusual_device', False):
            indicators.append('unusual_device')
        
        if transaction.get('rapid_transactions', False):
            indicators.append('velocity_anomaly')
        
        if transaction.get('suspicious_ip', False):
            indicators.append('suspicious_ip')
        
        timestamp = transaction.get('timestamp', datetime.now())
        if timestamp.hour < 6 or timestamp.hour > 22:
            indicators.append('unusual_time')
        
        return indicators
    
    def get_training_summary(self):
        """Get summary of training performance"""
        if not self.training_history:
            return "No training data available"
        
        recent_history = self.training_history[-100:]  # Last 100 episodes
        
        avg_reward = np.mean([h['total_reward'] for h in recent_history])
        avg_detection_rate = np.mean([h['detection_rate'] for h in recent_history])
        avg_false_positive_rate = np.mean([h['false_positives'] for h in recent_history]) / 100
        avg_customer_satisfaction = np.mean([h['customer_satisfaction'] for h in recent_history])
        
        return {
            'average_reward': avg_reward,
            'detection_rate': avg_detection_rate,
            'false_positive_rate': avg_false_positive_rate,
            'customer_satisfaction': avg_customer_satisfaction,
            'total_episodes': len(self.training_history),
            'q_table_size': len(self.agent.q_table)
        }

# Example usage and testing
def demo_threat_detection():
    """Demonstrate the threat detection system"""
    print("=== Banking App Threat Detection with Reinforcement Learning ===\n")
    
    # Initialize system
    threat_detector = ThreatDetectionSystem()
    
    # Train the system
    threat_detector.train(episodes=10000)
    
    print("\n=== Training Summary ===")
    summary = threat_detector.get_training_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
    
    print("\n=== Testing Threat Detection ===")
    
    # Test cases
    test_transactions = [
        {
            'amount': 100,
            'merchant_type': 'grocery',
            'location': 'home',
            'timestamp': datetime.now().replace(hour=14)
        },
        {
            'amount': 8000,
            'merchant_type': 'online',
            'location': 'foreign',
            'unusual_device': True,
            'timestamp': datetime.now().replace(hour=2)
        },
        {
            'amount': 9900,
            'merchant_type': 'transfer',
            'location': 'unknown',
            'rapid_transfers': True,
            'round_amounts': True,
            'timestamp': datetime.now().replace(hour=23)
        }
    ]
    
    test_labels = ['Legitimate Transaction', 'Card Fraud Attempt', 'Money Laundering Attempt']
    
    for i, (transaction, label) in enumerate(zip(test_transactions, test_labels)):
        print(f"\n--- {label} ---")
        result = threat_detector.predict_threat(transaction)
        
        print(f"Action: {result['action'].upper()}")
        print(f"Risk Score: {result['risk_score']:.3f}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Threat Indicators: {', '.join(result['threat_indicators']) if result['threat_indicators'] else 'None'}")

    # --- Plotting training metrics ---
    history = threat_detector.training_history
    episodes = [h['episode'] for h in history]
    rewards = [h['total_reward'] for h in history]
    detection_rates = [h['detection_rate'] for h in history]
    customer_satisfaction = [h['customer_satisfaction'] for h in history]

    plt.figure(figsize=(16, 5))

    plt.subplot(1, 3, 1)
    plt.plot(episodes, rewards, label='Reward', color='blue')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Reward per Episode')
    plt.grid(True)

    plt.subplot(1, 3, 2)
    plt.plot(episodes, detection_rates, label='Detection Rate', color='green')
    plt.xlabel('Episode')
    plt.ylabel('Detection Rate')
    plt.title('Detection Rate per Episode')
    plt.grid(True)

    plt.subplot(1, 3, 3)
    plt.plot(episodes, customer_satisfaction, label='Customer Satisfaction', color='orange')
    plt.xlabel('Episode')
    plt.ylabel('Customer Satisfaction')
    plt.title('Customer Satisfaction per Episode')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("training_metrics.png")
    plt.show()

    print(Fore.LIGHTGREEN_EX,"\nTraining completed successfully!",Style.RESET_ALL)
    print(Fore.RED,"Q-Table Size:", len(threat_detector.agent.q_table), Style.RESET_ALL)
    # Save the trained model
    with open('trained_agent.pkl', 'wb') as f:
        pickle.dump(threat_detector.agent, f)
    print(Fore.LIGHTGREEN_EX,"\nTrained agent saved to 'trained_agent.pkl'",Style.RESET_ALL)
if __name__ == "__main__":
    demo_threat_detection()

