import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

table_info = """
Create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), MARKS INT);
"""

cursor.execute(table_info)

cursor.execute("INSERT INTO STUDENT VALUES('Satyam', 'X', 90)")
cursor.execute("INSERT INTO STUDENT VALUES('Shivam', 'XI', 80)")
cursor.execute("INSERT INTO STUDENT VALUES('Rahul', 'XII', 85)")
cursor.execute("INSERT INTO STUDENT VALUES('Varun', 'X', 75)")

print("Data inserted successfully")

data = cursor.execute("SELECT * FROM STUDENT")

for row in data:
    print(row)

connection.commit()
connection.close()
