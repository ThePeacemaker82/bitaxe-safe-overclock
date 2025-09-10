#!/usr/bin/env python3
"""
Esempio di sweep interattivo che permette all'utente di scegliere
manualmente quali impostazioni applicare tra quelle migliori.
"""

import sys
import os
import csv
import time
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bitaxe_safe_overclock import BitAxeSafeOverclock, MINER_IP, SAFETY_CONFIG

def display_top_results(results, top_n=5):
    """Mostra i migliori risultati ordinati per efficienza"""
    if not results:
        print("❌ Nessun risultato disponibile")
        return
    
    # Ordina per efficienza (GH/W) decrescente
    sorted_results = sorted(results, key=lambda x: x['efficiency'], reverse=True)
    
    print(f"\n🏆 Top {min(top_n, len(sorted_results))} risultati (ordinati per efficienza):")
    print("=" * 80)
    
    for i, result in enumerate(sorted_results[:top_n], 1):
        status = "✅ STABILE" if result['stable'] else "❌ INSTABILE"
        vr_temp = result.get('vr_temperature', 'N/A')
        print(f"{i:2d}. {result['frequency']:3d}MHz @ {result['voltage']:4d}mV | "
              f"{result['hashrate']:6.2f} GH/s | {result['temperature']:5.1f}°C | "
              f"{result['power']:5.1f}W | {result['efficiency']:6.2f} GH/W | "
              f"VR: {vr_temp}°C | {status}")

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
        print(f"\n⚡ === Testando {voltage}mV - Sweep frequenze {freq_min}-{freq_max}MHz ===")  # ✅ CORRETTO
        
        for freq in range(freq_min, freq_max + 1, freq_step):
            current_test += 1
            print(f"\n🎯 Test {current_test}/{total_tests}: {freq}MHz @ {voltage}mV")
            
            # Applica le impostazioni
            if not overclock.apply_settings(freq, voltage):
                print(f"❌ Errore applicazione {freq}MHz @ {voltage}mV")
                continue
            
            # Attendi stabilizzazione
            print(f"⏱️ Attesa stabilizzazione {SAFETY_CONFIG['settle_time']}s...")
            time.sleep(SAFETY_CONFIG['settle_time'])
            
            # Test di stabilità
            stable, hashrates, mean_hashrate = overclock.test_stability(freq, voltage)
            
            # Ottieni stato finale
            state = overclock.get_current_state()
            if state:
                # Calcola efficienza
                efficiency = mean_hashrate / (state.power if state.power > 0 else 1)
                
                # Salva risultato
                result = {
                    'frequency': freq,
                    'core_voltage': voltage,
                    'hash_rate': mean_hashrate,
                    'temperature': state.temperature,
                    'power': state.power,
                    'efficiency': efficiency,
                    'stable': stable,
                    'samples': len(hashrates)
                }
                
                results.append(result)
                
                status = "✅ STABILE" if stable else "❌ INSTABILE"
                print(f"📈 Risultato: {mean_hashrate:.2f} GH/s, {state.temperature:.1f}°C, {efficiency:.2f} GH/J - {status}")
                
                # Se stabile, continua con frequenza successiva
                # Se instabile, probabilmente le frequenze successive falliranno anche
                if not stable:
                    print(f"⚠️ {freq}MHz instabile @ {voltage}mV - frequenze superiori probabilmente falliranno")
            else:
                print("❌ Errore lettura stato")
    
    return results

def main():
    print("🎮 Sweep Interattivo BitAxe")
    print(f"📡 Connessione a: {MINER_IP}")
    
    overclock = BitAxeSafeOverclock()
    
    try:
        # Backup impostazioni originali
        if not overclock.backup_original_settings():
            print("❌ Impossibile fare backup delle impostazioni originali")
            return 1
        
        print("\n⚙️ Configurazione sweep:")
        
        # Input parametri sweep con valori predefiniti dal SAFETY_CONFIG
        voltage_min = int(input(f"Voltaggio minimo (mV) [{SAFETY_CONFIG['cv_start']}]: ") or str(SAFETY_CONFIG['cv_start']))
        voltage_max = int(input(f"Voltaggio massimo (mV) [{SAFETY_CONFIG['cv_end']}]: ") or str(SAFETY_CONFIG['cv_end']))
        voltage_step = int(input(f"Step voltaggio (mV) [{SAFETY_CONFIG['cv_step']}]: ") or str(SAFETY_CONFIG['cv_step']))
        
        freq_min = int(input(f"Frequenza minima (MHz) [{SAFETY_CONFIG['freq_start']}]: ") or str(SAFETY_CONFIG['freq_start']))
        freq_max = int(input(f"Frequenza massima (MHz) [{SAFETY_CONFIG['freq_end']}]: ") or str(SAFETY_CONFIG['freq_end']))
        freq_step = int(input(f"Step frequenza (MHz) [{SAFETY_CONFIG['freq_step']}]: ") or str(SAFETY_CONFIG['freq_step']))
        
        test_duration = int(input(f"Durata test stabilità (sec) [{SAFETY_CONFIG['stability_test_duration']}]: ") or str(SAFETY_CONFIG['stability_test_duration']))
        
        # Validazione input
        if voltage_min < SAFETY_CONFIG['min_voltage'] or voltage_max > SAFETY_CONFIG['max_voltage']:
            print(f"❌ Voltaggio fuori dai limiti di sicurezza ({SAFETY_CONFIG['min_voltage']}-{SAFETY_CONFIG['max_voltage']}mV)")
            return 1
            
        if freq_min < SAFETY_CONFIG['min_frequency'] or freq_max > SAFETY_CONFIG['max_frequency']:
            print(f"❌ Frequenza fuori dai limiti di sicurezza ({SAFETY_CONFIG['min_frequency']}-{SAFETY_CONFIG['max_frequency']}MHz)")
            return 1
        
        # Esegui sweep personalizzato
        results = run_custom_sweep(
            overclock,
            (voltage_min, voltage_max, voltage_step),
            (freq_min, freq_max, freq_step),
            test_duration
        )
        
        if not results:
            print("\n❌ Nessun risultato ottenuto dallo sweep")
            return 1
        
        # Menu interattivo
        while True:
            display_top_results(results)
            
            print("\n🎯 Opzioni disponibili:")
            print("1. Applica le migliori impostazioni")
            print("2. Scegli dalle top 10")
            print("3. Mostra tutti i risultati")
            print("4. Salva risultati su CSV")
            print("5. Ripristina impostazioni originali")
            print("6. Esci")
            
            choice = input("\nScegli un'opzione (1-6): ").strip()
            
            if choice == "1":
                # Applica le migliori impostazioni (prima in classifica)
                best = sorted(results, key=lambda x: x['efficiency'], reverse=True)[0]
                print(f"\n🚀 Applicando: {best['frequency']}MHz @ {best['core_voltage']}mV")
                if overclock.apply_settings(best['frequency'], best['core_voltage']):
                    print("✅ Impostazioni applicate con successo!")
                    break
                else:
                    print("❌ Errore nell'applicazione delle impostazioni")
            
            elif choice == "2":
                # Scegli dalle top 10
                try:
                    rank = int(input("Inserisci il rank da applicare (1-10): "))
                    if 1 <= rank <= min(10, len(results)):
                        sorted_results = sorted(results, key=lambda x: x['efficiency'], reverse=True)
                        selected = sorted_results[rank-1]
                        print(f"\n🚀 Applicando: {selected['frequency']}MHz @ {selected['core_voltage']}mV")
                        if overclock.apply_settings(selected['frequency'], selected['core_voltage']):
                            print("✅ Impostazioni applicate con successo!")
                            break
                        else:
                            print("❌ Errore nell'applicazione delle impostazioni")
                    else:
                        print("❌ Rank non valido")
                except ValueError:
                    print("❌ Inserisci un numero valido")
            
            elif choice == "3":
                # Mostra tutti i risultati
                display_top_results(results, len(results))
            
            elif choice == "4":
                # Salva risultati
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"interactive_sweep_results_{timestamp}.csv"
                
                with open(filename, 'w', newline='') as csvfile:
                    fieldnames = ['timestamp', 'frequency', 'core_voltage', 'temperature', 'vr_temperature', 
                                'hash_rate', 'power', 'efficiency', 'shares_accepted', 'shares_rejected']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for result in results:
                        writer.writerow({
                            'timestamp': datetime.now().isoformat(),
                            'frequency': result['frequency'],
                            'core_voltage': result['core_voltage'],
                            'temperature': result['temperature'],
                            'vr_temperature': result['vr_temperature'],
                            'hash_rate': result['hash_rate'],
                            'power': result['power'],
                            'efficiency': result['efficiency'],
                            'shares_accepted': result['shares_accepted'],
                            'shares_rejected': result['shares_rejected']
                        })
                
                print(f"✅ Risultati salvati in: {filename}")
            
            elif choice == "5":
                # Ripristina impostazioni originali
                if overclock.restore_original_settings():
                    print("✅ Impostazioni originali ripristinate")
                    break
                else:
                    print("❌ Errore nel ripristino delle impostazioni")
            
            elif choice == "6":
                print("👋 Uscita...")
                break
            
            else:
                print("❌ Opzione non valida")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Interruzione utente")
        return 1
    except Exception as e:
        print(f"❌ Errore: {e}")
        return 1
    finally:
        # Cleanup sempre eseguito
        if overclock.original_settings:
            overclock.restore_original_settings()
        
        return 0

if __name__ == "__main__":
    exit(main())