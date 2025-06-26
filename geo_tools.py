import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import os

def generate_stylized_maps(csv_path, geojson_path, output_folder="stylized_maps", missing_txt_path="missing.txt"):
    """
    Genera mappe stilizzate bianche in PNG per i paesi elencati in un CSV,
    utilizzando i dati di un GeoJSON. Traccia i paesi per cui non è possibile generare una mappa.

    Args:
        csv_path (str): Percorso al file CSV contenente i nomi dei paesi.
        geojson_path (str): Percorso al file GeoJSON contenente la geometria dei paesi.
        output_folder (str): Nome della cartella dove salvare le immagini PNG generate.
        missing_txt_path (str): Nome del file di testo per elencare i paesi mancanti.
    """
    
    print(f"Inizio generazione mappe stilizzate...")

    # Assicurati che la cartella di output esista
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Creata cartella di output: '{output_folder}'")

    # Lista per tenere traccia dei paesi mancanti
    missing_countries = []

    try:
        # 1. Leggi i nomi dei paesi dal file CSV
        # Assumiamo che la prima colonna contenga i nomi dei paesi
        countries_df = pd.read_csv(csv_path, header=None) # header=None se il CSV non ha intestazione
        country_names = countries_df.iloc[:, 0].astype(str).tolist() # Prende la prima colonna
        print(f"Letti {len(country_names)} nomi di paesi da '{csv_path}'")

    except FileNotFoundError:
        print(f"Errore: File CSV non trovato al percorso '{csv_path}'")
        return
    except Exception as e:
        print(f"Errore durante la lettura del CSV: {e}")
        return

    try:
        # 2. Carica il file GeoJSON
        world = geopandas.read_file(geojson_path)
        print(f"Caricato file GeoJSON da '{geojson_path}'")
    except FileNotFoundError:
        print(f"Errore: File GeoJSON non trovato al percorso '{geojson_path}'")
        return
    except Exception as e:
        print(f"Errore durante il caricamento del GeoJSON: {e}")
        return

    # Itera sui nomi dei paesi letti dal CSV
    for country_name in country_names:
        # Pulisci il nome del paese per usarlo nel nome del file
        # Sostituisci spazi e caratteri speciali con underscore e converti in minuscolo
        safe_country_name = country_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")

        output_png_file = os.path.join(output_folder, f"{safe_country_name}.png")

        # Cerca il paese nel GeoJSON (case-insensitive)
        # Assumiamo che il nome del paese sia nella colonna 'name' o 'NAME'
        # Adatta 'name' se il tuo GeoJSON usa una colonna diversa per i nomi dei paesi
        found_country = world[world['name'].str.lower() == country_name.lower()]

        if not found_country.empty:
            # Se il paese è stato trovato, genera la mappa
            try:
                fig, ax = plt.subplots(1, 1, figsize=(10, 10)) # Dimensione immagine
                
                # Plotta il paese in bianco con bordo nero
                found_country.plot(ax=ax, color='white', edgecolor='black', linewidth=0.7)

                ax.set_title(f'Map of {country_name}', fontsize=0) # Titolo invisibile
                ax.set_axis_off() # Nascondi gli assi per una mappa pulita

                plt.savefig(output_png_file, dpi=300, bbox_inches='tight', pad_inches=0.1, transparent=True)
                plt.close(fig) # Chiudi il plot per liberare memoria
                print(f"Generata mappa per '{country_name}' -> '{output_png_file}'")
            except Exception as e:
                print(f"Errore durante la generazione della mappa per '{country_name}': {e}")
                missing_countries.append(country_name)
            except Exception as e:
                print(f"Errore durante la generazione della mappa per '{country_name}': {e}")
                missing_countries.append(country_name)
        else:
            # Se il paese non è stato trovato, aggiungilo alla lista dei mancanti
            print(f"Paese '{country_name}' non trovato nel GeoJSON.")
            missing_countries.append(country_name)

    # Scrivi la lista dei paesi mancanti nel file missing.txt
    if missing_countries:
        with open(missing_txt_path, 'w', encoding='utf-8') as f:
            for country in missing_countries:
                f.write(f"{country}\n")
        print(f"\nGenerato '{missing_txt_path}' con {len(missing_countries)} paesi mancanti.")
    else:
        print("\nNessun paese mancante rilevato.")
        if os.path.exists(missing_txt_path):
            os.remove(missing_txt_path) # Rimuovi il file se non ci sono mancanti
            print(f"Rimosso '{missing_txt_path}' (nessun paese mancante).")

    print("\nProcesso completato.")

# --- Esempio di Utilizzo ---
if __name__ == "__main__":
    # Assicurati che questi percorsi siano corretti per i tuoi file
    csv_input = 'countries_data.csv'  # Il tuo file CSV
    geojson_input = 'countries.geojson' # Il tuo file GeoJSON

    # Nota: Assicurati di avere i file 'countries_data.csv' e 'countries.geojson'
    # nella stessa directory dello script, o di fornire i percorsi completi.
    # Puoi trovare questi file nel repository Geo-guess-game.

    # Per un test veloce se non hai i file:
    # Crea un dummy countries_data.csv
    if not os.path.exists(csv_input):
        with open(csv_input, 'w') as f:
            f.write("United States\n")
            f.write("Canada\n")
            f.write("Mexico\n")
            f.write("Atlantis\n") # Questo sarà un paese mancante per il test

    # Esegui la funzione
    generate_stylized_maps(csv_input, geojson_input)

    # Per un esempio con un CSV che ha un'intestazione
    # Se il tuo CSV ha un'intestazione, potresti voler modificare la riga:
    # countries_df = pd.read_csv(csv_path, header=None)
    # a:
    # countries_df = pd.read_csv(csv_path)
    # e poi selezionare la colonna per nome:
    # country_names = countries_df['Nome_Colonna_Paesi'].astype(str).tolist()