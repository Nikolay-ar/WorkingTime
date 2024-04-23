import sqlite3

# con = sqlite3.connect('db.sqlite')
con = sqlite3.connect('dd\customdb.sqlite')
cur = con.cursor()

# Дорогой SQL, верни все столбцы всех записей из таблицы movies;
# символ * после SELECT означает "верни все поля найденных записей".
# cur.execute(
# SELECT name,
# release_year
#      '''
# SELECT gross,
#        type,
#        name,
#        release_year
# FROM movies
# ORDER BY type DESC, name
# LIMIT 12 OFFSET 0
# ;''')


# cur.execute(   
# ''' DELETE FROM timing_1 WHERE id = (SELECT MAX(ID) FROM timing_1) ''')
# con.commit()

# ''' UPDATE timing set endTime = null WHERE id = (SELECT MAX(ID) FROM timing) ''')
# con.commit()

# cur.execute(   
# ''' UPDATE timing_1 set startTime = '08:05:04' WHERE id = 1 ''')
# con.commit()



# cur.execute(f"SELECT count(*) FROM timing_1")


# cur.execute(    
#      '''
# SELECT id, dw, day, startTime, endTime, dw 
# FROM timing_1''')

cur.execute(    
     '''
SELECT * FROM timing_1
''')

# cur.execute("SELECT COUNT(*) FROM timing_1 WHERE id >= (SELECT MAX(id) FROM timing_1 WHERE dw = 1) ")

# cur.execute("SELECT MAX(id) FROM timing_1 WHERE dw = 1 ")

# cur.execute("PRAGMA table_info(timing_1);")
# print(cur.fetchall())

# Python превращает результирующую выборку в итерируемый объект,
# который можно перебрать циклом:
for result in cur:
    print(result)

# При получении данных из таблицы коммит не нужен.
con.close()
