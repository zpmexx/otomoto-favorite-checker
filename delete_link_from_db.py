import sqlite3
from datetime import datetime
import sys
from pathlib import Path

try:
    file_name = Path(__file__).stem
except:
    file_name = None

now = formatDateTime = formatted_date = formatDbDateTime = None
try:
    now = datetime.now()
    formatDateTime = now.strftime("%d/%m/%Y %H:%M")
    formatDbDateTime = now.strftime("%Y/%m/%d %H:%M")
    formatted_date = now.strftime("%Y-%m-%d")
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""Problem with date - {str(e)}\n""")

try:
    conn = sqlite3.connect('cars.db')
    cursor = conn.cursor()
except Exception as e:
    with open('logfile.log', 'a') as file:
        file.write(f"{formatDateTime}  {file_name} Problem with db: {e}\n")
    sys.exit(0)

link = input("Paste auction's link to delete from db: ")

try:
    title = cursor.execute('SELECT title from cars where link = ?', (link,)).fetchone()
    deleted_count = cursor.execute("DELETE from cars where link = ?",(link,)).rowcount
    conn.commit()
    if deleted_count>0:
        print(f"Deleted from database {title} auction's link: {link}")
        with open ("deleted_from_db.log",'a') as file:
            file.write(f"{formatDateTime} Deleted from database {title} auction's link: {link}\n")
    else:
        print(f"Cannot delete {link} from database - link doesn't exists.")
except Exception as e:
    print(f"Cannot delete {link} from database - {e}")
    with open ("deleted_from_db.log",'a') as file:
        file.write(f"{formatDateTime} Could not delete auction: {link} - {e}\n")
