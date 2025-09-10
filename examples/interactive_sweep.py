#!/usr/bin/env python3
"""
Esempio di sweep interattivo che permette all'utente di scegliere
manualmente quali impostazioni applicare tra quelle migliori.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bitaxe_safe_overclock import BitAxeSafeOverclock
import time

def display_top_results(results, top_n=5):
    """Mostra i migliori N risultati"""
    if not results:
        print("Nessun risultato disponibile")
        return
        
    # Ordina per efficienza (GH/J)
    sorted_results = sorted(results, key=lambda x: x.get('efficiency', 0), reverse=True)
    
    print(f"\n🏆 Top {min(top_n, len(sorted_results))} configurazioni per efficienza:")
    print("─" * 80)
    print(f"{'#':<3} {'Volt':<6} {'Freq':<6} {'Hash':<8} {'Eff':<8} {'Temp':<6} {'Stabile':<8}")
    print("─" * 80)
    
    for i, result in enumerate(sorted_results[:top_n], 1):
        stable = "✅ Sì" if result.get('stable', False) else "❌ No"
        print(f"{i:<3} {result['voltage']:<6} {result['frequency']:<6} "
              f"{result['hashrate']:<8.2f} {result['efficiency']:<8.2f} "
              f"{result['temperature']:<6} {stable:<8}")

def main():
    miner_ip = "192.168.1.100"  # Sostituire con l'IP del proprio BitAxe
    
    print("🎮 Sweep Interattivo BitAxe")
    print(f"📡 Connessione a: {miner_ip}")
    
    overclock = BitAxeSafeOverclock(miner_ip)
    
    try:
        # Configurazione sweep
        print("\n⚙️ Configurazione sweep:")
        voltage_min = int(input("Voltaggio minimo (mV) [1100]: ") or "1100")
        voltage_max = int(input("Voltaggio massimo (mV) [1300]: ") or "1300")
        voltage_step = int(input("Step voltaggio (mV) [25]: ") or "25")
        
        freq_min = int(input("Frequenza minima (MHz) [400]: ") or "400")
        freq_max = int(input("Frequenza massima (MHz) [600]: ") or "600")
        freq_step = int(input("Step frequenza (MHz) [25]: ") or "25")
        
        test_duration = int(input("Durata test (secondi) [300]: ") or "300")
        
        print(f"\n🚀 Avvio sweep: {voltage_min}-{voltage_max}mV, {freq_min}-{freq_max}MHz")
        
        # Esegui sweep SENZA applicare automaticamente
        results = overclock.sweep_optimization(
            voltage_range=(voltage_min, voltage_max, voltage_step),
            frequency_range=(freq_min, freq_max, freq_step),
            test_duration=test_duration,
            apply_best=False  # Non applicare automaticamente
        )
        
        print(f"\n✅ Sweep completato! Testati {len(results)} configurazioni")
        
        # Mostra i migliori risultati
        display_top_results(results, 10)
        
        # Menu interattivo
        while True:
            print("\n🎯 Opzioni disponibili:")
            print("1. Applica la configurazione migliore automaticamente")
            print("2. Scegli una configurazione specifica")
            print("3. Mostra tutti i risultati")
            print("4. Salva risultati su file")
            print("5. Esci")
            
            choice = input("\nScegli un'opzione (1-5): ")
            
            if choice == "1":
                best = overclock.find_best_settings(results)
                if best:
                    print(f"\n🏆 Applicazione migliore configurazione:")
                    print(f"   {best['voltage']}mV, {best['frequency']}MHz")
                    
                    confirm = input("Confermi? (s/N): ")
                    if confirm.lower() in ['s', 'si', 'y', 'yes']:
                        if overclock.apply_settings(best['voltage'], best['frequency']):
                            print("✅ Impostazioni applicate!")
                            break
                        else:
                            print("❌ Errore nell'applicazione")
                else:
                    print("❌ Nessuna configurazione stabile trovata")
                    
            elif choice == "2":
                display_top_results(results, 10)
                try:
                    idx = int(input("\nScegli il numero della configurazione (1-10): ")) - 1
                    sorted_results = sorted(results, key=lambda x: x.get('efficiency', 0), reverse=True)
                    
                    if 0 <= idx < len(sorted_results):
                        selected = sorted_results[idx]
                        print(f"\n⚡ Configurazione selezionata:")
                        print(f"   {selected['voltage']}mV, {selected['frequency']}MHz")
                        
                        confirm = input("Applicare? (s/N): ")
                        if confirm.lower() in ['s', 'si', 'y', 'yes']:
                            if overclock.apply_settings(selected['voltage'], selected['frequency']):
                                print("✅ Impostazioni applicate!")
                                break
                            else:
                                print("❌ Errore nell'applicazione")
                    else:
                        print("❌ Numero non valido")
                except ValueError:
                    print("❌ Inserire un numero valido")
                    
            elif choice == "3":
                display_top_results(results, len(results))
                
            elif choice == "4":
                filename = overclock.save_results(results)
                print(f"💾 Risultati salvati in: {filename}")
                
            elif choice == "5":
                print("👋 Uscita...")
                break
                
            else:
                print("❌ Opzione non valida")
                
    except Exception as e:
        print(f"❌ Errore: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())