# Ethical Hacking Portal

A Flask-based web application for testing website security against various attack patterns from the NSL-KDD dataset.

## Overview

The Ethical Hacking Portal allows users to:

1. Simulate various attack types against a specified website
2. Monitor real-time status of the attack simulation
3. View detailed results and analysis of the website's security response
4. Learn about different attack patterns and their characteristics

## Features

- **Attack Simulation**: Simulate different attack types with adjustable intensity
- **Real-time Monitoring**: Track requests sent, blocked, and overall block rate
- **Detailed Analysis**: Get insights into the effectiveness of the target website's security
- **Educational Resources**: Learn about different attack patterns from the NSL-KDD dataset

## Prerequisites

- Python 3.7+
- Flask
- Pandas
- Scikit-learn
- Requests
- NSL-KDD dataset

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ethical-hacking-portal.git
   cd ethical-hacking-portal
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download the NSL-KDD dataset:
   - Go to: [NSL-KDD Dataset](https://www.kaggle.com/datasets/hassan06/nslkdd)
   - Download KDDTrain+.txt
   - Rename it to nsl_kdd.csv and place it inside the dataset/ folder

## Usage

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Enter the target website URL, select an attack type, and adjust the intensity.

4. Click "Start Simulation" to begin the test.

5. Monitor the real-time status and view the results.

## Attack Types

The portal supports various attack types from the NSL-KDD dataset:

- **Neptune**: SYN flood DoS attack
- **Smurf**: ICMP echo request DoS attack
- **Portsweep**: Port scanning reconnaissance
- **Satan**: Vulnerability scanning tool
- **IPsweep**: Network host discovery
- **Nmap**: Port scanning tool
- **Back**: Web server DoS attack
- **Teardrop**: Fragmented packet DoS attack
- **Pod**: Ping of Death attack
- **Warezclient**: Illegal content download client
- **Normal**: Regular, non-malicious traffic

## Ethical Considerations

This tool is intended for educational purposes and ethical security testing only. Only use it on websites you own or have explicit permission to test. Unauthorized testing is illegal and unethical.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NSL-KDD dataset creators
- Flask and its contributors
- The cybersecurity community for educational resources
