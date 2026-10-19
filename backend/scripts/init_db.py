"""Initialize DATABASE_URL schema safely; repeat without resetting learner data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.wecode.sql_storage import SQLStorage, database_url

if __name__ == '__main__':
    storage = SQLStorage(database_url())
    storage.close()
    print('PASS database schema initialization; no learner data reset')
