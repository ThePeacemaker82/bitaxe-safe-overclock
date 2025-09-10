#!/usr/bin/env python3
"""
Esempio di applicazione delle migliori impostazioni da un file CSV esistente.
Utile quando si hanno già dei risultati di sweep precedenti.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bitaxe_safe_overclock import BitAxeSafeOverclock
import argparse

def main():
    parser = argparse.ArgumentParser(description='Applica le migliori impostazioni da file CSV')
    parser.add_argument('csv_file', help='File CSV con i risultati del sweep')
    parser.add_argument('--ip', default='192.168.1.100', help='IP del BitAxe')
    parser.add_argument('--dry-run', action='store_true', help='Mostra solo le impostazioni senza applicarle')
    
    args = parser.parse_args()
    
    print(f"📊 Analisi file CSV: {args.csv_file}")
    print(f"📡 BitAxe IP: {args.ip}")
    
    # Inizializza il sistema
    overclock = BitAxeSafeOverclock(args.ip)
    
    try:
        # Carica e analizza i risultati dal CSV
        print("\n🔍 Caricamento risultati dal CSV...")
        results = overclock.load_results_from_csv(args.csv_file)
        
        if not results:
            print("❌ Nessun risultato trovato nel file CSV")
            return 1
            
        print(f"✅ Caricati {len(results)} risultati")
        
        # Trova le migliori impostazioni
        best_settings = overclock.find_best_settings(results)
        
        if not best_settings:
            print("⚠️ Nessuna configurazione stabile trovata nei risultati")
            return 1
            
        # Mostra le impostazioni migliori
        print(f"\n🏆 Migliori impostazioni trovate:")
        print(f"   Voltaggio: {best_settings['voltage']}mV")
        print(f"   Frequenza: {best_settings['frequency']}MHz")
        print(f"   Hashrate: {best_settings['hashrate']:.2f} GH/s")
        print(f"   Efficienza: {best_settings['efficiency']:.2f} GH/J")
        print(f"   Temperatura: {best_settings['temperature']}°C")
        
        if args.dry_run:
            print("\n🔍 Modalità dry-run: impostazioni NON applicate")
            return 0
            
        # Chiedi conferma all'utente
        response = input("\n❓ Applicare queste impostazioni al miner? (s/N): ")
        if response.lower() not in ['s', 'si', 'y', 'yes']:
            print("❌ Operazione annullata dall'utente")
            return 0
            
        # Applica le impostazioni
        print("\n⚡ Applicazione impostazioni...")
        success = overclock.apply_best_settings(results)
        
        if success:
            print("✅ Impostazioni applicate con successo!")
            
            # Verifica le impostazioni applicate
            print("\n🔍 Verifica impostazioni applicate...")
            current_state = overclock.get_current_state()
            print(f"   Voltaggio attuale: {current_state.voltage}mV")
            print(f"   Frequenza attuale: {current_state.frequency}MHz")
        else:
            print("❌ Errore nell'applicazione delle impostazioni")
            return 1
            
    except FileNotFoundError:
        print(f"❌ File CSV non trovato: {args.csv_file}")
        return 1
    except Exception as e:
        print(f"❌ Errore: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())