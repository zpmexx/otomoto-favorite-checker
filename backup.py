import sqlite3
from datetime import datetime
from pathlib import Path
try:
    file_name = Path(__file__).stem
except:
    file_name = None


#get date
now = formatDateTime = formatted_date = formatDbDateTime = None
try:
    now = datetime.now()
    formatDateTime = now.strftime("%d/%m/%Y %H:%M")
    formatDbDateTime = now.strftime("%Y/%m/%d %H:%M")
    formatted_date = now.strftime("%Y-%m-%d")
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{file_name} - Problem with date - {str(e)}\n""")


original_db = "cars.db"
backup_db = f"backup/{formatted_date}-backup-cars.db"

try:
    with sqlite3.connect(original_db) as source_conn:
        with sqlite3.connect(backup_db) as dest_conn:
            source_conn.backup(dest_conn)
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{file_name} - Problem with date - {str(e)}\n""")
