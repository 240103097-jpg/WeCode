"""Create ignored project data directory/schema; never copy, delete or reset a DB."""
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from backend.wecode.sql_storage import SQLStorage

if __name__=='__main__':
    (ROOT/'data').mkdir(exist_ok=True)
    storage=SQLStorage(os.environ.get('DATABASE_URL','sqlite:///'+str(ROOT/'data/wecode.sqlite3')))
    storage.close()
    print('PASS local schema/content prepared without resetting learner records; project data directory retained')
