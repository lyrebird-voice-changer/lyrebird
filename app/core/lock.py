import fcntl
from pathlib import Path

lock_file_path = Path(Path('/tmp') / 'lyrebird.lock')
def place_lock():
    '''
    Places a lockfile file in the user's home directory to prevent
    two instances of Lyrebird running at once.

    Returns lock file to be closed before application close, if
    `None` returned then lock failed and another instance of
    Lyrebird is most likely running.
    '''
    lock_file = open(lock_file_path, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except:
        return None
    return lock_file

def destroy_lock():
    '''
    Destroy the lock file. Should close lock file before running.
    '''
    if lock_file_path.exists():
        lock_file_path.unlink()
