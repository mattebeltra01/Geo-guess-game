import sqlite3
import csv
import pandas as pd # Importato per leggere il CSV in modo più robusto
import os

def create_database_with_image_paths(csv_file_path, output_image_folder="stylized_maps", db_name='geo_game_data.db', table_name='country_info'):
    """
    Crea un database SQLite da un file CSV e aggiunge una colonna per il percorso
    previsto dell'immagine stilizzata di ogni paese.

    Args:
        csv_file_path (str): Percorso al file CSV contenente i dati dei paesi.
        output_image_folder (str): Nome della cartella dove si prevede siano salvate le immagini.
        db_name (str): Nome del file del database SQLite da creare.
        table_name (str): Nome della tabella nel database.
    """
    print(f"--- Creazione del database '{db_name}' e della tabella '{table_name}' ---")
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 1. Leggi il CSV con pandas per gestire meglio i nomi delle colonne
        # Assumiamo che la prima colonna del CSV sia il nome del paese.
        # Se il tuo CSV ha un'intestazione, pandas la leggerà automaticamente.
        # Se non ha intestazione, puoi specificare header=None e poi rinominare le colonne.
        countries_df = pd.read_csv(csv_file_path) # Legge il CSV, pandas inferisce le intestazioni
        
        # Assumiamo che la prima colonna sia il nome del paese. 
        # Puoi modificarlo se il nome del paese è in una colonna specifica.
        country_name_col = countries_df.columns[0] 

        # Aggiungi una nuova colonna per il percorso dell'immagine
        # Normalizza il nome del paese per costruire il path dell'immagine
        countries_df['image_path'] = countries_df[country_name_col].apply(
            lambda name: os.path.join(output_image_folder, 
                                      f"{name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')}.png")
        )
        
        # 2. Crea la tabella nel database
        # Converti i tipi di colonna di pandas in tipi SQLite
        column_definitions = []
        for col_name, dtype in countries_df.dtypes.items():
            if dtype == 'int64':
                sqlite_type = 'INTEGER'
            elif dtype == 'float64':
                sqlite_type = 'REAL'
            else: # Per stringhe, bool, ecc.
                sqlite_type = 'TEXT'
            column_definitions.append(f"{col_name.replace(' ', '_')} {sqlite_type}") # Sostituisci spazi nei nomi colonna
        
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"
        cursor.execute(create_table_sql)
        print(f"Tabella '{table_name}' creata o già esistente.")

        # 3. Inserisci i dati dal DataFrame nel database
        # Converti il DataFrame in una lista di tuple per l'inserimento
        data_to_insert = [tuple(row) for row in countries_df.values]

        # Prepara la query INSERT dinamica
        columns = ', '.join([col.replace(' ', '_') for col in countries_df.columns])
        placeholders = ', '.join(['?' for _ in countries_df.columns])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

        # Esegui l'inserimento batch
        cursor.executemany(insert_sql, data_to_insert)
        conn.commit()
        print(f"Dati importati con successo da '{csv_file_path}' in '{db_name}'.")
        print(f"Aggiunta colonna 'image_path' con i percorsi delle immagini.")

    except FileNotFoundError:
        print(f"Errore: File CSV non trovato al percorso '{csv_file_path}'")
    except pd.errors.EmptyDataError:
        print(f"Errore: Il file CSV '{csv_file_path}' è vuoto.")
    except sqlite3.Error as e:
        print(f"Errore del database: {e}")
    except Exception as e:
        print(f"Si è verificato un errore inatteso: {e}")
    finally:
        if conn:
            conn.close()
            print("Connessione al database chiusa.")

# --- Esempio di Utilizzo ---
if __name__ == "__main__":
    # Assicurati che 'countries_data.csv' esista e contenga dati.
    # Ad esempio, dal repository Geo-guess-game:
    # https://github.com/mattebeltra01/Geo-guess-game/blob/main/countries_data.csv <sup data-citation="5"><a href="#" title="Reference 5 (source not available)">5</a></sup>
    
    csv_file = 'countries_data.csv'
    output_db = 'geo_game_with_images.db'
    image_folder = 'stylized_maps' # La cartella dove salvi le immagini PNG

    # Esegui la funzione per creare il database
    create_database_with_image_paths(csv_file, image_folder, output_db)

    # Puoi anche verificare il contenuto del database (opzionale)
    print("\n--- Verifica contenuto database ---")
    conn_check = None
    try:
        conn_check = sqlite3.connect(output_db)
        cursor_check = conn_check.cursor()
        cursor_check.execute(f"SELECT * FROM country_info LIMIT 5;") # Mostra le prime 5 righe
        rows = cursor_check.fetchall()
        column_names = [description[0] for description in cursor_check.description]
        print(f"Colonne: {column_names}")
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Errore durante la verifica del database: {e}")
    finally:
        if conn_check:
            conn_check.close()