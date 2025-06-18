import numpy as np
import time
import random
from datetime import datetime

class FeatureExtractor:
    def __init__(self):
        """Initialize the feature extractor"""
        self.protocol_map = {
            'http': 'tcp',
            'https': 'tcp',
            'ftp': 'tcp',
            'ssh': 'tcp',
            'telnet': 'tcp',
            'smtp': 'tcp',
            'dns': 'udp',
            'ntp': 'udp',
            'icmp': 'icmp'
        }
        
        self.service_map = {
            'http': 'http',
            'https': 'http',
            'ftp': 'ftp',
            'ssh': 'ssh',
            'telnet': 'telnet',
            'smtp': 'smtp',
            'dns': 'domain_u',
            'ntp': 'ntp_u'
        }
        
        # Connection flags
        self.flags = ['S0', 'S1', 'SF', 'REJ', 'RSTO', 'RSTR', 'SH']
    
    def extract_features(self, request_data, attack_type='normal'):
        """
        Extract NSL-KDD features from a request
        
        Parameters:
        - request_data: Dictionary containing request information
        - attack_type: Type of attack to simulate
        
        Returns:
        - features: List of 41 features matching NSL-KDD format
        """
        # Initialize features array
        features = [0] * 41
        
        # Basic features (1-9)
        features[0] = request_data.get('duration', random.randint(0, 100))  # duration
        
        # Protocol type
        protocol = request_data.get('protocol', 'http').lower()
        features[1] = self.protocol_map.get(protocol, 'tcp')  # protocol_type
        
        # Service
        service = request_data.get('service', protocol).lower()
        features[2] = self.service_map.get(service, 'private')  # service
        
        # Flag
        features[3] = request_data.get('flag', random.choice(self.flags))  # flag
        
        # Source and destination bytes
        features[4] = request_data.get('src_bytes', random.randint(100, 1000))  # src_bytes
        features[5] = request_data.get('dst_bytes', random.randint(100, 10000))  # dst_bytes
        
        # Other basic features
        features[6] = request_data.get('land', 0)  # land
        features[7] = request_data.get('wrong_fragment', 0)  # wrong_fragment
        features[8] = request_data.get('urgent', 0)  # urgent
        
        # Content features (10-22)
        # These are mostly related to content of the connection
        features[9] = request_data.get('hot', 0)  # hot
        features[10] = request_data.get('num_failed_logins', 0)  # num_failed_logins
        features[11] = request_data.get('logged_in', 0)  # logged_in
        features[12] = request_data.get('num_compromised', 0)  # num_compromised
        features[13] = request_data.get('root_shell', 0)  # root_shell
        features[14] = request_data.get('su_attempted', 0)  # su_attempted
        features[15] = request_data.get('num_root', 0)  # num_root
        features[16] = request_data.get('num_file_creations', 0)  # num_file_creations
        features[17] = request_data.get('num_shells', 0)  # num_shells
        features[18] = request_data.get('num_access_files', 0)  # num_access_files
        features[19] = request_data.get('num_outbound_cmds', 0)  # num_outbound_cmds
        features[20] = request_data.get('is_host_login', 0)  # is_host_login
        features[21] = request_data.get('is_guest_login', 0)  # is_guest_login
        
        # Time-based traffic features (23-31)
        features[22] = request_data.get('count', random.randint(1, 20))  # count
        features[23] = request_data.get('srv_count', random.randint(1, 20))  # srv_count
        features[24] = request_data.get('serror_rate', random.random())  # serror_rate
        features[25] = request_data.get('srv_serror_rate', random.random())  # srv_serror_rate
        features[26] = request_data.get('rerror_rate', random.random())  # rerror_rate
        features[27] = request_data.get('srv_rerror_rate', random.random())  # srv_rerror_rate
        features[28] = request_data.get('same_srv_rate', random.random())  # same_srv_rate
        features[29] = request_data.get('diff_srv_rate', random.random())  # diff_srv_rate
        features[30] = request_data.get('srv_diff_host_rate', random.random())  # srv_diff_host_rate
        
        # Host-based traffic features (32-41)
        features[31] = request_data.get('dst_host_count', random.randint(1, 255))  # dst_host_count
        features[32] = request_data.get('dst_host_srv_count', random.randint(1, 255))  # dst_host_srv_count
        features[33] = request_data.get('dst_host_same_srv_rate', random.random())  # dst_host_same_srv_rate
        features[34] = request_data.get('dst_host_diff_srv_rate', random.random())  # dst_host_diff_srv_rate
        features[35] = request_data.get('dst_host_same_src_port_rate', random.random())  # dst_host_same_src_port_rate
        features[36] = request_data.get('dst_host_srv_diff_host_rate', random.random())  # dst_host_srv_diff_host_rate
        features[37] = request_data.get('dst_host_serror_rate', random.random())  # dst_host_serror_rate
        features[38] = request_data.get('dst_host_srv_serror_rate', random.random())  # dst_host_srv_serror_rate
        features[39] = request_data.get('dst_host_rerror_rate', random.random())  # dst_host_rerror_rate
        features[40] = request_data.get('dst_host_srv_rerror_rate', random.random())  # dst_host_srv_rerror_rate
        
        # Modify features based on attack type
        self._adjust_features_for_attack(features, attack_type)
        
        return features
    
    def _adjust_features_for_attack(self, features, attack_type):
        """Adjust feature values to match characteristics of the specified attack type"""
        if attack_type == 'normal':
            # Normal traffic has balanced features
            return
            
        elif attack_type == 'neptune':
            # SYN flood attack
            features[1] = 'tcp'  # protocol_type
            features[3] = 'S0'   # flag (SYN without completion)
            features[24] = random.uniform(0.8, 1.0)  # serror_rate
            features[25] = random.uniform(0.8, 1.0)  # srv_serror_rate
            features[37] = random.uniform(0.8, 1.0)  # dst_host_serror_rate
            features[38] = random.uniform(0.8, 1.0)  # dst_host_srv_serror_rate
            
        elif attack_type == 'smurf':
            # ICMP echo reply flood
            features[1] = 'icmp'  # protocol_type
            features[2] = 'ecr_i'  # service
            features[4] = 1032    # src_bytes (typical for smurf)
            features[5] = 0       # dst_bytes
            features[22] = random.randint(200, 500)  # count (high)
            features[23] = random.randint(200, 500)  # srv_count (high)
            
        elif attack_type == 'portsweep':
            # Port scanning
            features[1] = 'tcp'  # protocol_type
            features[3] = 'REJ'  # flag (many rejected connections)
            features[26] = random.uniform(0.8, 1.0)  # rerror_rate
            features[27] = random.uniform(0.8, 1.0)  # srv_rerror_rate
            features[29] = random.uniform(0.8, 1.0)  # diff_srv_rate (many different services)
            
        elif attack_type == 'satan':
            # Network scanning tool
            features[1] = 'tcp'  # protocol_type
            features[2] = 'private'  # service
            features[3] = 'REJ'  # flag
            features[26] = random.uniform(0.8, 1.0)  # rerror_rate
            features[29] = random.uniform(0.8, 1.0)  # diff_srv_rate
            
        elif attack_type == 'ipsweep':
            # IP sweep reconnaissance
            features[1] = 'icmp'  # protocol_type
            features[2] = 'eco_i'  # service
            features[4] = 8       # src_bytes
            features[5] = 0       # dst_bytes
            
        elif attack_type == 'teardrop':
            # Teardrop attack (fragmentation)
            features[1] = 'udp'  # protocol_type
            features[7] = 3      # wrong_fragment
            
        # Add more attack types as needed
