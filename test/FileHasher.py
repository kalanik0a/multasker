import hashlib
import os
import sqlite3
import multiprocessing

from multasker.process import TwoQueue

class FileHasher(TwoQueue):
    path = ''
    @staticmethod
    def hash_file(filepath):
        """Calculate the SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            file_size_bytes = os.path.getsize(filepath)
            chunk_size = 4096
            with open(filepath, "rb") as f:
                
                read_size = chunk_size
                file_size = 'tiny'
                if file_size_bytes < chunk_size:
                    read_size = file_size_bytes
                elif chunk_size < file_size_bytes < (1024 * 1024 * 1024):
                    read_size = file_size_bytes if file_size_bytes < (1024 * 1024 * 32) else 1024 * 1024 * 32
                    file_size = 'small'
                elif file_size_bytes >= (1024 * 1024 * 1024 * 10):
                    read_size = 1024 * 1024 * 128
                    file_size = 'huge'
                elif file_size_bytes >= (1024 * 1024 * 1024):
                    read_size = 1024 * 1024 * 32
                    file_size = 'large'
                print(f"[INFO] Hashing [{file_size}] {filepath}")
                for chunk in iter(lambda: f.read(read_size), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error hashing file {filepath}: {e}")
            return None
  
    @staticmethod
    def worker(task_queue, result_queue, existing_paths):
        """Worker process to process files from the task queue."""
        while True:
            task = task_queue.get()
            if task is None:  # Stop condition
                break
            #print(f"[INFO] processing {task[0]}")
            directory, files = task
            for file in files:
                filepath = os.path.join(directory, file)
                 # Skip if file path is already in the existing_paths set
                if filepath in existing_paths:
                    # print(f"Skipping {filepath}")
                    continue
                """
                if FileHasher.is_cloud_file(filepath=filepath):
                    print(f"[INFO] Skipping {filepath}. Cloud-only file")
                    continue
                """
                file_hash = FileHasher.hash_file(filepath)
                if file_hash:  # Only add if hash calculation was successful
                    result_queue.put((filepath, file_hash))
                else:
                    result_queue.put((filepath, ''))
  
    @staticmethod
    def db_writer(result_queue, db_path="file_hashes.db", batch_size=1000):
        """DB writer process that batches results from the result queue and writes to SQLite."""
        # Connect to the SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paths (
                path TEXT PRIMARY KEY,
                hash TEXT
            )
        """)
        conn.commit()

        batch = []
        while True:
            try:
                result = result_queue.get(timeout=5)  # Wait for a result
                if result is None:  # Stop condition
                    if batch:
                        FileHasher.write_to_db(cursor, batch)
                        conn.commit()
                    break

                batch.append(result)

                # If batch size is reached, write to the database
                if len(batch) >= batch_size:
                    FileHasher.write_to_db(cursor, batch)
                    conn.commit()
                    batch.clear()
            except multiprocessing.queues.Empty:
                pass  # If no items in the queue, continue (or handle timeout)

        conn.close()
  
    @staticmethod
    def write_to_db(cursor, batch):
        """Write a batch of results to the SQLite database."""
        try:
            cursor.executemany("""
                INSERT OR REPLACE INTO paths (path, hash) VALUES (?, ?)
            """, batch)
            print("[INFO] Wrote results to database")
        except sqlite3.Error as e:
            print(f"Error writing to DB: {e}")
    
    @staticmethod
    def queue_callback(task_queue):
      # Add tasks to the task queue from os.walk
      for root, _, files in os.walk(FileHasher.path):
          if files:  # Only add entries that have files
              task_queue.put((root, files))
    
    @staticmethod
    def set_path(pathname=''):
      FileHasher.path = pathname
      
    @staticmethod
    def load_existing_paths(db_path="file_hashes.db"):
        """Load existing file paths from the database into a set."""
        existing_paths = set()
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Get all file paths from the database
                cursor.execute("SELECT path FROM paths")
                rows = cursor.fetchall()

                # Add each file path to the set
                existing_paths = {row[0] for row in rows}

                conn.close()
                print(f"Loaded {len(existing_paths)} existing file paths from the database.")
            except sqlite3.Error as e:
                print(f"Error reading from DB: {e}")
        else:
            print("No existing database found; starting fresh.")

        return existing_paths