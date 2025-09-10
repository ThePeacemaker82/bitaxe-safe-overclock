#!/usr/bin/env python3
"""
Script di monitoraggio continuo delle performance dopo l'applicazione
delle impostazioni ottimali.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bitaxe_safe_overclock import BitAxeSafeOverclock
import time
import signal
import csv
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, miner_ip, log_file=None):
        self.miner_ip = miner_ip  # Salviamo l'IP per riferimento
        self.overclock = BitAxeSafeOverclock()  # Rimuovo il parametro miner_ip
        self.running = True
        self.log_file = log_file or f"performance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Gestione segnali per uscita pulita
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        print("\n🛑 Arresto monitoraggio...")
        self.running = False
        
    def monitor(self, interval=60, duration=None):
        """Monitora le performance per un periodo specificato"""
        print(f"📊 Avvio monitoraggio performance")
        print(f"📝 Log file: {self.log_file}")
        print(f"⏱️ Intervallo: {interval} secondi")
        if duration:
            print(f"⏰ Durata: {duration} secondi")
        print("\nPremi Ctrl+C per fermare il monitoraggio\n")
        
        start_time = time.time()
        
        # Inizializza file CSV
        with open(self.log_file, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'voltage', 'frequency', 'hashrate', 'temperature', 'power', 'efficiency']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            while self.running:
                try:
                    # Ottieni stato attuale
                    state = self.overclock.get_current_state()
                    
                    # Calcola efficienza
                    efficiency = state.hash_rate / state.power if state.power > 0 else 0  # Cambiato da state.hashrate
                    
                    # Log dati
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'voltage': state.core_voltage,  # Cambiato da state.voltage
                        'frequency': state.frequency,
                        'hashrate': state.hash_rate,  # Cambiato da state.hashrate
                        'temperature': state.temperature,
                        'power': state.power,
                        'efficiency': efficiency
                    }
                    
                    writer.writerow(log_entry)
                    csvfile.flush()
                    
                    # Mostra stato corrente
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | "
                          f"🔋 {state.core_voltage}mV | "  # Cambiato da state.voltage
                          f"⚡ {state.frequency}MHz | "
                          f"⛏️ {state.hash_rate:.2f}GH/s | "  # Cambiato da state.hashrate
                          f"🌡️ {state.temperature}°C | "
                          f"💡 {state.power:.1f}W | "
                          f"📈 {efficiency:.2f}GH/J")
                    
                    # Controllo temperatura di sicurezza
                    if state.temperature > 85:
                        print(f"🚨 ATTENZIONE: Temperatura alta ({state.temperature}°C)!")
                        
                    # Controllo durata
                    if duration and (time.time() - start_time) >= duration:
                        print(f"\n⏰ Durata monitoraggio completata ({duration}s)")
                        break
                        
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"❌ Errore durante il monitoraggio: {e}")
                    time.sleep(interval)
                    
        print(f"\n📊 Monitoraggio completato. Log salvato in: {self.log_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitora le performance del BitAxe')
    parser.add_argument('--ip', default='192.168.1.100', help='IP del BitAxe')
    parser.add_argument('--interval', type=int, default=60, help='Intervallo di monitoraggio in secondi')
    parser.add_argument('--duration', type=int, help='Durata totale in secondi (infinito se non specificato)')
    parser.add_argument('--log-file', help='File di log personalizzato')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(args.ip, args.log_file)
    monitor.monitor(args.interval, args.duration)

if __name__ == "__main__":
    main()