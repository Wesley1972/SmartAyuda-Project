import sqlite3

conn = sqlite3.connect('todo.db')
conn.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, tasks TEXT)''')

while True:
    choice = input("\n1. Add task \n2. View Tasks \n3. Delete Task \n4. Exit \nChoose: ");

    if choice == '1':
        task = input("Enter Task: ")
        conn.execute('''INSERT INTO tasks (tasks) VALUES (?)''', (task,))

    elif choice == '2':
        for row in conn.execute('SELECT * FROM tasks'):
            print(row[0], "-", row[1])

    elif choice == '3':
        task_id = input("Enter tasks ID to delete: ")
        conn.execute('''DELETE FROM tasks WHERE id = ?''', (task_id,))
        conn.commit()

    elif choice == '4':
        break
conn.close()

