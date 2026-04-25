import sqlite3

conn = sqlite3.connect("sqlite.db")
c = conn.cursor()

# c.execute('SELECT * FROM portfolios')
# for row in c.fetchall():
#     print({
#         'id': row[0],
#         'uuid': row[1],
#         'name': row[2],
#         'bio': row[3],
#         'github': row[4],
#         'telegram': row[5],
#         'avatar': row[6],
#         'skills': row[7].split(",") if row[7] else []
#     })

# Добавляем колонку 'tags' с дефолтным значением '[]'
c.execute("ALTER TABLE portfolios ADD COLUMN tools TEXT DEFAULT '[]'")

# Обязательно сохраняем изменения
c.commit()


conn.close()