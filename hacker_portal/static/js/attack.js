// Attack Simulation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Attack type descriptions for tooltips
    const attackDescriptions = {
        'neptune': 'A SYN flood DoS attack that sends a lot of SYN packets to a server but never completes the TCP handshake.',
        'smurf': 'A DoS attack that uses ICMP echo request packets (pings) with a spoofed source address.',
        'portsweep': 'A reconnaissance attack that scans ports to find services running on a host.',
        'satan': 'A network scanning tool that looks for known vulnerabilities.',
        'ipsweep': 'A surveillance sweep to determine which hosts are listening on a network.',
        'nmap': 'A port scanning tool used to discover hosts and services on a network.',
        'normal': 'Regular, non-malicious network traffic.',
        'back': 'An attack against web servers that causes denial of service.',
        'teardrop': 'A DoS attack that sends fragmented packets that can\'t be reassembled properly.',
        'pod': 'Ping of Death - an attack that sends malformed or oversized ping packets.',
        'warezclient': 'A client that connects to a warezserver to download illegal content.'
    };
    
    // Attack type selection
    const attackTypeSelect = document.getElementById('attack-type');
    if (attackTypeSelect) {
        attackTypeSelect.addEventListener('change', function() {
            const selectedAttack = this.value;
            const description = attackDescriptions[selectedAttack.toLowerCase()] || 'No description available';
            
            // Update attack description if element exists
            const attackDescription = document.getElementById('attack-description');
            if (attackDescription) {
                attackDescription.textContent = description;
            }
            
            // Adjust intensity recommendation based on attack type
            adjustIntensityRecommendation(selectedAttack);
        });
    }
    
    // Intensity slider
    const intensitySlider = document.getElementById('attack-intensity');
    if (intensitySlider) {
        intensitySlider.addEventListener('input', function() {
            updateIntensityLabel(this.value);
        });
        
        // Initialize intensity label
        updateIntensityLabel(intensitySlider.value);
    }
    
    // Functions
    function adjustIntensityRecommendation(attackType) {
        const intensitySlider = document.getElementById('attack-intensity');
        if (!intensitySlider) return;
        
        // Set recommended intensity based on attack type
        let recommendedIntensity = 5; // Default
        
        switch (attackType.toLowerCase()) {
            case 'neptune':
            case 'smurf':
                // DoS attacks typically use higher intensity
                recommendedIntensity = 7;
                break;
            case 'portsweep':
            case 'ipsweep':
            case 'satan':
            case 'nmap':
                // Scanning attacks use medium intensity
                recommendedIntensity = 5;
                break;
            case 'normal':
                // Normal traffic uses lower intensity
                recommendedIntensity = 3;
                break;
            case 'teardrop':
            case 'pod':
                // These attacks can be effective at lower intensities
                recommendedIntensity = 4;
                break;
            default:
                recommendedIntensity = 5;
        }
        
        intensitySlider.value = recommendedIntensity;
        updateIntensityLabel(recommendedIntensity);
    }
    
    function updateIntensityLabel(value) {
        const intensityValue = parseInt(value);
        let intensityLabel = '';
        
        if (intensityValue <= 3) {
            intensityLabel = 'Low';
        } else if (intensityValue <= 7) {
            intensityLabel = 'Medium';
        } else {
            intensityLabel = 'High';
        }
        
        // Update label if element exists
        const intensityDisplay = document.getElementById('intensity-display');
        if (intensityDisplay) {
            intensityDisplay.textContent = `${intensityLabel} (${intensityValue})`;
        }
    }
    
    // Attack cards click handler
    const attackCards = document.querySelectorAll('.attack-type-card');
    attackCards.forEach(card => {
        card.addEventListener('click', function() {
            const attackType = this.dataset.attack;
            
            // Set the attack type in the select box if it exists
            if (attackTypeSelect) {
                attackTypeSelect.value = attackType;
                
                // Trigger change event to update description
                const event = new Event('change');
                attackTypeSelect.dispatchEvent(event);
                
                // Scroll to form
                document.getElementById('attack-form').scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
