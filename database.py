import sqlite3

FILENAME = 'final.db'

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(FILENAME, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_books(self):
        data = self.cursor.execute("SELECT * FROM book;").fetchall()
        data = [{
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "pages": book[3],
            "rating": book[4]
            } for book in data
        ]
        return data

    def add_book(self, book):
        curr = self.cursor.execute("SELECT MAX(id) FROM book;").fetchone()[0]
        if curr == None:
            new_id = 0
        else:
            new_id = curr + 1

        self.cursor.execute("INSERT INTO book VALUES(?, ?, ?, ?, ?);", 
            (new_id,
            book["title"], 
            book["author"], 
            book["pages"],
            book["rating"]
            )   
        )
        self.conn.commit()
        return

    def delete_book(self, id):
        self.cursor.execute("DELETE FROM book WHERE id=?;", (id,))
        self.conn.commit()

def create_database():
    with open(FILENAME, 'w'):
        pass

    conn = sqlite3.connect(FILENAME)
    cursor = conn.cursor()

    schema = """
    CREATE TABLE book(
        id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        pages INTEGER,
        ratings TEXT
    );
    """
    
    cursor.executescript(schema)

    cursor.close()
    conn.commit()

if __name__ == "__main__":
    create_database()