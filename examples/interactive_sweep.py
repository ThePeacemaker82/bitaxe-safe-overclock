#!/usr/bin/env python3
"""
Esempio di sweep interattivo che permette all'utente di scegliere
manualmente quali impostazioni applicare tra quelle migliori.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bitaxe_safe_overclock import BitAxeSafeOverclock, MINER_IP, SAFETY_CONFIG
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

def run_custom_sweep(overclock, voltage_range, frequency_range, test_duration):
    """Esegue uno sweep personalizzato frequency-first e restituisce i risultati"""
    results = []
    voltage_min, voltage_max, voltage_step = voltage_range
    freq_min, freq_max, freq_step = frequency_range
    
    print(f"\n🚀 Avvio sweep frequency-first...")
    print(f"📊 Range: {voltage_min}-{voltage_max}mV, {freq_min}-{freq_max}MHz")
    
    total_tests = len(range(voltage_min, voltage_max + 1, voltage_step)) * len(range(freq_min, freq_max + 1, freq_step))
    current_test = 0
    
    # LOGICA CORRETTA: Prima voltaggio, poi frequenza (frequency-first)
    for voltage in range(voltage_min, voltage_max + 1, voltage_step):
        print(f"\n⚡ === Testando {voltage}mV - Sweep frequenze {freq_min}-{freq_max}MHz ===\")
        
        for freq in range(freq_min, freq_max + 1, freq_step):
            current_test += 1
            print(f"\n🎯 Test {current_test}/{total_tests}: {freq}MHz @ {voltage}mV\")
            
            # Applica le impostazioni
            if not overclock.apply_settings(freq, voltage):
                print(f"❌ Errore applicazione {freq}MHz @ {voltage}mV\")
                continue
            
            # Attendi stabilizzazione
            print(f"⏱️ Attesa stabilizzazione {SAFETY_CONFIG['settle_time']}s...\")
            time.sleep(SAFETY_CONFIG['settle_time'])
            
            # Test di stabilità
            stable, hashrates, mean_hashrate = overclock.test_stability(freq, voltage)
            
            # Ottieni stato finale
            state = overclock.get_current_state()
            if state:
                efficiency = mean_hashrate / (state.power if state.power > 0 else 1)
                
                result = {
                    'frequency': freq,
                    'voltage': voltage,
                    'hashrate': mean_hashrate,
                    'temperature': state.temperature,
                    'power': state.power,
                    'efficiency': efficiency,
                    'stable': stable,
                    'samples': len(hashrates)
                }
                
                results.append(result)
                
                status = \"✅ Stabile\" if stable else \"❌ Instabile\"
                print(f\"📈 Risultato: {mean_hashrate:.2f} GH/s, {state.temperature:.1f}°C, {efficiency:.2f} GH/J - {status}\")
                
                # Se stabile, continua con frequenza successiva
                # Se instabile, probabilmente le frequenze successive falliranno anche
                if not stable:
                    print(f\"⚠️ {freq}MHz instabile @ {voltage}mV - frequenze superiori probabilmente falliranno\")
            else:
                print(\"❌ Errore lettura stato\")
    
    return results

def main():
    print("🎮 Sweep Interattivo BitAxe")
    print(f"📡 Connessione a: {MINER_IP}")
    
    overclock = BitAxeSafeOverclock()
    
    try:
        # Backup impostazioni originali
        if not overclock.backup_original_settings():
            print("❌ Errore backup impostazioni originali")
            return 1
        
        # Configurazione sweep
        print("\n⚙️ Configurazione sweep:")
        voltage_min = int(input(f"Voltaggio minimo (mV) [{SAFETY_CONFIG['cv_start']}]: ") or str(SAFETY_CONFIG['cv_start']))
        voltage_max = int(input(f"Voltaggio massimo (mV) [{SAFETY_CONFIG['cv_max']}]: ") or str(SAFETY_CONFIG['cv_max']))
        voltage_step = int(input(f"Step voltaggio (mV) [{SAFETY_CONFIG['cv_step']}]: ") or str(SAFETY_CONFIG['cv_step']))
        
        freq_min = int(input(f"Frequenza minima (MHz) [{SAFETY_CONFIG['freq_start']}]: ") or str(SAFETY_CONFIG['freq_start']))
        freq_max = int(input(f"Frequenza massima (MHz) [{SAFETY_CONFIG['freq_end']}]: ") or str(SAFETY_CONFIG['freq_end']))
        freq_step = int(input(f"Step frequenza (MHz) [{SAFETY_CONFIG['freq_step']}]: ") or str(SAFETY_CONFIG['freq_step']))
        
        test_duration = int(input(f"Durata test (secondi) [{SAFETY_CONFIG['stability_interval'] * SAFETY_CONFIG['stability_samples']}]: ") or str(SAFETY_CONFIG['stability_interval'] * SAFETY_CONFIG['stability_samples']))
        
        # Esegui sweep personalizzato
        results = run_custom_sweep(
            overclock,
            (voltage_min, voltage_max, voltage_step),
            (freq_min, freq_max, freq_step),
            test_duration
        )
        
        print(f"\n✅ Sweep completato! Testati {len(results)} configurazioni")
        
        if not results:
            print("❌ Nessun risultato ottenuto")
            return 1
        
        # Mostra i migliori risultati
        display_top_results(results, 10)
        
        # Menu interattivo
        while True:
            print("\n🎯 Opzioni disponibili:")
            print("1. Applica la configurazione migliore automaticamente")
            print("2. Scegli una configurazione specifica")
            print("3. Mostra tutti i risultati")
            print("4. Salva risultati su file")
            print("5. Ripristina impostazioni originali")
            print("6. Esci")
            
            choice = input("\nScegli un'opzione (1-6): ")
            
            if choice == "1":
                # Trova la migliore configurazione stabile
                stable_results = [r for r in results if r['stable']]
                if stable_results:
                    best = max(stable_results, key=lambda x: x['efficiency'])
                    print(f"\n🏆 Applicazione migliore configurazione:")
                    print(f"   {best['voltage']}mV, {best['frequency']}MHz")
                    print(f"   {best['hashrate']:.2f} GH/s, {best['efficiency']:.2f} GH/J")
                    
                    confirm = input("Confermi? (s/N): ")
                    if confirm.lower() in ['s', 'si', 'y', 'yes']:
                        if overclock.apply_settings(best['frequency'], best['voltage']):
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
                        print(f"   {selected['hashrate']:.2f} GH/s, {selected['efficiency']:.2f} GH/J")
                        print(f"   Stabile: {'✅ Sì' if selected['stable'] else '❌ No'}")
                        
                        confirm = input("Applicare? (s/N): ")
                        if confirm.lower() in ['s', 'si', 'y', 'yes']:
                            if overclock.apply_settings(selected['frequency'], selected['voltage']):
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
                # Salva risultati manualmente
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"interactive_sweep_results_{timestamp}.csv"
                
                try:
                    with open(filename, 'w', newline='') as csvfile:
                        fieldnames = ['frequency', 'voltage', 'hashrate', 'temperature', 'power', 'efficiency', 'stable', 'samples']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        for result in results:
                            writer.writerow(result)
                    print(f"💾 Risultati salvati in: {filename}")
                except Exception as e:
                    print(f"❌ Errore salvataggio: {e}")
                
            elif choice == "5":
                if overclock.restore_original_settings():
                    print("🔄 Impostazioni originali ripristinate")
                else:
                    print("❌ Errore ripristino impostazioni")
                    
            elif choice == "6":
                print("👋 Uscita...")
                break
                
            else:
                print("❌ Opzione non valida")
                
    except KeyboardInterrupt:
        print("\n⚠️ Interruzione utente")
        overclock.restore_original_settings()
        return 1
    except Exception as e:
        print(f"❌ Errore: {e}")
        overclock.restore_original_settings()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())