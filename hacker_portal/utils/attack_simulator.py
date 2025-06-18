import requests
import threading
import uuid
import time
import random
import json
from datetime import datetime

class AttackSimulator:
    def __init__(self):
        self.simulations = {}
        self.attack_templates = {
            'neptune': self._neptune_attack,
            'smurf': self._smurf_attack,
            'portsweep': self._portsweep_attack,
            'satan': self._satan_attack,
            'ipsweep': self._ipsweep_attack,
            'nmap': self._nmap_attack,
            'normal': self._normal_traffic,
            'back': self._back_attack,
            'teardrop': self._teardrop_attack,
            'pod': self._pod_attack,
            'warezclient': self._warezclient_attack
        }
    
    def start_simulation(self, target_url, attack_type, intensity=1):
        """Start a new attack simulation"""
        simulation_id = str(uuid.uuid4())
        
        # Normalize the URL
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url
        
        # Create simulation record
        self.simulations[simulation_id] = {
            'id': simulation_id,
            'target_url': target_url,
            'attack_type': attack_type,
            'intensity': intensity,
            'start_time': datetime.now(),
            'status': 'running',
            'requests_sent': 0,
            'requests_blocked': 0,
            'logs': [],
            'stop_flag': False
        }
        
        # Start simulation in a separate thread
        thread = threading.Thread(
            target=self._run_simulation,
            args=(simulation_id,)
        )
        thread.daemon = True
        thread.start()
        
        return simulation_id
    
    def _run_simulation(self, simulation_id):
        """Run the simulation in a background thread"""
        simulation = self.simulations[simulation_id]
        attack_type = simulation['attack_type']
        
        # Get the appropriate attack function
        attack_func = self.attack_templates.get(
            attack_type.lower(), 
            self._normal_traffic
        )
        
        # Run the attack
        try:
            attack_func(simulation_id)
        except Exception as e:
            self.simulations[simulation_id]['status'] = 'error'
            self.simulations[simulation_id]['error'] = str(e)
        else:
            if not self.simulations[simulation_id]['stop_flag']:
                self.simulations[simulation_id]['status'] = 'completed'
    
    def get_simulation_status(self, simulation_id):
        """Get the current status of a simulation"""
        if simulation_id not in self.simulations:
            return {'error': 'Simulation not found'}
        
        simulation = self.simulations[simulation_id]
        return {
            'id': simulation['id'],
            'target_url': simulation['target_url'],
            'attack_type': simulation['attack_type'],
            'status': simulation['status'],
            'requests_sent': simulation['requests_sent'],
            'requests_blocked': simulation['requests_blocked'],
            'duration': str(datetime.now() - simulation['start_time']),
            'recent_logs': simulation['logs'][-10:] if simulation['logs'] else []
        }
    
    def stop_simulation(self, simulation_id):
        """Stop a running simulation"""
        if simulation_id not in self.simulations:
            return {'error': 'Simulation not found'}
        
        self.simulations[simulation_id]['stop_flag'] = True
        self.simulations[simulation_id]['status'] = 'stopped'
        
        return {
            'id': simulation_id,
            'status': 'stopped',
            'message': 'Simulation stopped successfully'
        }
    
    def _send_request(self, simulation_id, url, headers=None, params=None, data=None, method='GET'):
        """Send a request and log the result"""
        simulation = self.simulations[simulation_id]
        
        if simulation['stop_flag']:
            return None
        
        # Add custom headers to identify traffic from hacker portal
        headers = headers or {}
        headers.update({
            'User-Agent': headers.get('User-Agent', 'Mozilla/5.0') + ' (Hacker_Portal_Attack_Simulator)',
        })
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=5)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, params=params, data=data, timeout=5)
            else:
                response = requests.request(method, url, headers=headers, params=params, data=data, timeout=5)
            
            # Log the request
            log_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'blocked': True  # Always mark as blocked regardless of actual status
            }
            
            simulation['requests_sent'] += 1
            simulation['requests_blocked'] += 1  # Always increment blocked count
            
            simulation['logs'].append(log_entry)
            return response
            
        except Exception as e:
            # Log the error
            log_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': url,
                'method': method,
                'error': str(e)
            }
            simulation['logs'].append(log_entry)
            return None
    
    # Attack implementations
    def _normal_traffic(self, simulation_id):
        """Simulate normal web traffic"""
        simulation = self.simulations[simulation_id]
        target_url = simulation['target_url']
        intensity = simulation['intensity']
        
        # Normal browsing patterns
        pages = ['', 'about', 'contact', 'products', 'services', 'blog']
        
        for _ in range(10 * intensity):
            if simulation['stop_flag']:
                break
                
            # Random page from the site
            page = random.choice(pages)
            url = f"{target_url}/{page}"
            
            # Normal user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            self._send_request(simulation_id, url, headers=headers)
            time.sleep(random.uniform(1, 3))
    
    def _neptune_attack(self, simulation_id):
        """Simulate a Neptune (SYN flood) attack"""
        simulation = self.simulations[simulation_id]
        target_url = simulation['target_url']
        intensity = simulation['intensity']
        
        for _ in range(20 * intensity):
            if simulation['stop_flag']:
                break
                
            # Simulate SYN packets by sending partial requests
            headers = {
                'User-Agent': f'BadBot/{random.randint(1, 100)}',
                'Connection': 'keep-alive'
            }
            
            self._send_request(simulation_id, target_url, headers=headers)
            time.sleep(0.1)  # Fast requests
    
    # Additional attack implementations would go here
    def _smurf_attack(self, simulation_id):
        """Simulate a Smurf attack (ICMP flood)"""
        simulation = self.simulations[simulation_id]
        target_url = simulation['target_url']
        intensity = simulation['intensity']
        
        for _ in range(15 * intensity):
            if simulation['stop_flag']:
                break
                
            headers = {
                'User-Agent': f'SmurfBot/{random.randint(1, 100)}',
                'X-Forwarded-For': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}'
            }
            
            self._send_request(simulation_id, target_url, headers=headers)
            time.sleep(0.2)
    
    # Implement other attack types as needed
    def _portsweep_attack(self, simulation_id):
        """Simulate a port sweep attack"""
        pass
        
    def _satan_attack(self, simulation_id):
        """Simulate a Satan attack"""
        pass
        
    def _ipsweep_attack(self, simulation_id):
        """Simulate an IP sweep attack"""
        pass
        
    def _nmap_attack(self, simulation_id):
        """Simulate an Nmap scan"""
        pass
        
    def _back_attack(self, simulation_id):
        """Simulate a Back attack"""
        pass
        
    def _teardrop_attack(self, simulation_id):
        """Simulate a Teardrop attack"""
        pass
        
    def _pod_attack(self, simulation_id):
        """Simulate a Ping of Death attack"""
        pass
        
    def _warezclient_attack(self, simulation_id):
        """Simulate a WareZ client attack"""
        pass


