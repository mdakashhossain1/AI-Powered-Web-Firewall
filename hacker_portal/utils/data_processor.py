import pandas as pd
import numpy as np
import os

class DataProcessor:
    def __init__(self, dataset_path):
        """Initialize the data processor with the NSL-KDD dataset"""
        self.dataset_path = dataset_path
        self.column_names = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
            'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
            'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
            'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
            'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
            'dst_host_srv_count', 'dst_host_same_srv_rate',
            'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
            'dst_host_srv_rerror_rate', 'attack_type'
        ]
        
        # Load the dataset if it exists
        if os.path.exists(dataset_path):
            self.df = pd.read_csv(dataset_path, header=None)
            if len(self.df.columns) == len(self.column_names):
                self.df.columns = self.column_names
            else:
                # Handle case where column count doesn't match
                self.df.columns = list(range(self.df.shape[1]))
                self.df.rename(columns={self.df.columns[-1]: 'attack_type'}, inplace=True)
        else:
            # Create an empty dataframe with the expected columns
            self.df = pd.DataFrame(columns=self.column_names)
    
    def get_attack_types(self):
        """Get a list of unique attack types from the dataset"""
        if self.df.empty:
            return []
        
        attack_types = self.df['attack_type'].unique().tolist()
        # Sort with 'normal' first, then alphabetically
        attack_types.sort()
        if 'normal' in attack_types:
            attack_types.remove('normal')
            attack_types.insert(0, 'normal')
        
        return attack_types
    
    def get_attack_details(self, attack_type):
        """Get details about a specific attack type"""
        if self.df.empty or attack_type not in self.df['attack_type'].values:
            return {
                'name': attack_type,
                'count': 0,
                'description': 'No information available',
                'features': {}
            }
        
        # Filter for the specific attack type
        attack_df = self.df[self.df['attack_type'] == attack_type]
        
        # Get average values for numeric features
        numeric_features = attack_df.select_dtypes(include=[np.number]).columns
        feature_averages = {col: float(attack_df[col].mean()) for col in numeric_features}
        
        # Get most common values for categorical features
        categorical_features = ['protocol_type', 'service', 'flag']
        for col in categorical_features:
            if col in attack_df.columns:
                feature_averages[col] = attack_df[col].value_counts().index[0]
        
        # Attack descriptions
        attack_descriptions = {
            'normal': 'Regular, non-malicious network traffic.',
            'neptune': 'A SYN flood DoS attack that sends a lot of SYN packets to a server but never completes the TCP handshake.',
            'smurf': 'A DoS attack that uses ICMP echo request packets (pings) with a spoofed source address.',
            'portsweep': 'A reconnaissance attack that scans ports to find services running on a host.',
            'satan': 'A network scanning tool that looks for known vulnerabilities.',
            'ipsweep': 'A surveillance sweep to determine which hosts are listening on a network.',
            'nmap': 'A port scanning tool used to discover hosts and services on a network.',
            'back': 'An attack against web servers that causes denial of service.',
            'teardrop': 'A DoS attack that sends fragmented packets that can\'t be reassembled properly.',
            'pod': 'Ping of Death - an attack that sends malformed or oversized ping packets.',
            'warezclient': 'A client that connects to a warezserver to download illegal content.',
            'warezmaster': 'A server offering illegal content for download.',
            'land': 'A DoS attack that sends a packet with the same source and destination IP and port.',
            'rootkit': 'A collection of tools that enable administrator-level access to a computer or network.'
        }
        
        return {
            'name': attack_type,
            'count': len(attack_df),
            'description': attack_descriptions.get(attack_type, 'No description available'),
            'features': feature_averages
        }
    
    def get_dataset_stats(self):
        """Get general statistics about the dataset"""
        if self.df.empty:
            return {
                'total_records': 0,
                'attack_distribution': {},
                'protocol_distribution': {}
            }
        
        # Count records by attack type
        attack_counts = self.df['attack_type'].value_counts().to_dict()
        
        # Count records by protocol type
        if 'protocol_type' in self.df.columns:
            protocol_counts = self.df['protocol_type'].value_counts().to_dict()
        else:
            protocol_counts = {}
        
        return {
            'total_records': len(self.df),
            'attack_distribution': attack_counts,
            'protocol_distribution': protocol_counts
        }
    
    def get_attack_features(self, attack_type):
        """Get feature vectors for a specific attack type"""
        if self.df.empty or attack_type not in self.df['attack_type'].values:
            return []
        
        # Get a sample of records for the attack type
        attack_samples = self.df[self.df['attack_type'] == attack_type].sample(
            min(10, self.df[self.df['attack_type'] == attack_type].shape[0])
        )
        
        # Convert to list of dictionaries
        samples = []
        for _, row in attack_samples.iterrows():
            sample = row.to_dict()
            samples.append(sample)
        
        return samples
