#!/usr/bin/env python3
"""
Esempio di sweep con applicazione automatica delle impostazioni migliori.
Questo script esegue un sweep completo e applica automaticamente le impostazioni
che hanno dato i migliori risultati.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bitaxe_safe_overclock import BitAxeSafeOverclock
import time

def main():
    # Configurazione del miner
    miner_ip = "192.168.1.100"  # Sostituire con l'IP del proprio BitAxe
    
    print("🚀 Avvio sweep con applicazione automatica delle impostazioni migliori")
    print(f"📡 Connessione a BitAxe: {miner_ip}")
    
    # Inizializza il sistema di overclocking sicuro
    overclock = BitAxeSafeOverclock(miner_ip)
    
    try:
        # Esegui sweep con range personalizzato
        print("\n⚡ Avvio sweep di ottimizzazione...")
        results = overclock.sweep_optimization(
            voltage_range=(1100, 1300, 25),  # Da 1.1V a 1.3V, step 25mV
            frequency_range=(400, 600, 25),   # Da 400MHz a 600MHz, step 25MHz
            test_duration=300,                # 5 minuti per test
            apply_best=True                   # Applica automaticamente le migliori impostazioni
        )
        
        print(f"\n✅ Sweep completato! Testati {len(results)} configurazioni")
        
        # Trova e mostra le impostazioni migliori
        best_settings = overclock.find_best_settings(results)
        if best_settings:
            print(f"\n🏆 Migliori impostazioni trovate:")
            print(f"   Voltaggio: {best_settings['voltage']}mV")
            print(f"   Frequenza: {best_settings['frequency']}MHz")
            print(f"   Hashrate: {best_settings['hashrate']:.2f} GH/s")
            print(f"   Efficienza: {best_settings['efficiency']:.2f} GH/J")
            print(f"   Temperatura: {best_settings['temperature']}°C")
            
            print("\n🎯 Impostazioni applicate automaticamente al miner!")
        else:
            print("\n⚠️ Nessuna configurazione stabile trovata")
            
    except Exception as e:
        print(f"\n❌ Errore durante il sweep: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())