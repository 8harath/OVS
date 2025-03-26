import sqlite3
from sqlite3 import Error
import os

def create_connection():
    conn = None
    try:
        # Get the absolute path to the database file
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'voting_system.db'))
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        print(f"Attempting to connect to database at: {db_path}")  # Debug print
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to the database at {db_path}")
        return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        print(f"Current working directory: {os.getcwd()}")  # Debug print
        print(f"Directory contents: {os.listdir()}")  # Debug print
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(f"Error creating table: {e}")

def init_db():
    database = r"database/voting_system.db"

    sql_create_voters_table = """ CREATE TABLE IF NOT EXISTS voters (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    last_name text NOT NULL,
                                    date_of_birth text NOT NULL,
                                    phone_number text NOT NULL,
                                    voter_id text NOT NULL UNIQUE,
                                    password text NOT NULL,
                                    has_voted integer DEFAULT 0
                                ); """

    sql_create_candidates_table = """CREATE TABLE IF NOT EXISTS candidates (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    party text NOT NULL,
                                    photo_url text NOT NULL,
                                    promises text NOT NULL,
                                    assets text NOT NULL,
                                    liabilities text NOT NULL,
                                    background text NOT NULL,
                                    political_views text NOT NULL,
                                    regional_views text NOT NULL
                                );"""

    sql_create_votes_table = """CREATE TABLE IF NOT EXISTS votes (
                                id integer PRIMARY KEY,
                                voter_id integer NOT NULL,
                                candidate_id integer NOT NULL,
                                timestamp text NOT NULL,
                                reference_number text NOT NULL UNIQUE,
                                FOREIGN KEY (voter_id) REFERENCES voters (id),
                                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
                            );"""

    conn = create_connection()

    if conn is not None:
        create_table(conn, sql_create_voters_table)
        create_table(conn, sql_create_candidates_table)
        create_table(conn, sql_create_votes_table)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    init_db()