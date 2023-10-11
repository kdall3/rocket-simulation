import sqlite3

from rocket_parts import *
import file_handler

DATABASE = 'rockets.db'
BLACKLISTED_ATTRIBUTES = ['being_dragged', 'selected', 'mass_override', 'hit_box', 'vertices', 'colour', 'parent']
INT_ATTRIBUTES = ['local_part_id', 'parent_id', 'fin_count']
TEXT_ATTRIBUTES = ['cone_shape', 'fin_shape']


def get_attributes(object):
    return([attr for attr in dir(object) if not callable(getattr(object, attr)) and not attr.startswith("__")])


def connect(db_path):
    return(sqlite3.connect(db_path))


def execute_sql(conn, sql):
    c = conn.cursor()
    command = sql.split(' ')[0].upper()

    c.execute(sql)
    if command == 'INSERT':
        conn.commit()
    elif command == 'DELETE':
        conn.commit()
    elif command =='SELECT':
        return c.fetchall()


def init_db():
    conn = connect(DATABASE)

    sql = "CREATE TABLE IF NOT EXISTS Rocket (rocket_id INTEGER PRIMARY KEY, name TEXT);"
    execute_sql(conn, sql)

    for rocket_part in ROCKET_PARTS:
        attributes = vars(rocket_part()).keys()
        attributes_to_save = []
        for attr in attributes:
            if attr not in BLACKLISTED_ATTRIBUTES:
                if attr in INT_ATTRIBUTES:
                    attr += ' INTEGER'
                elif attr in TEXT_ATTRIBUTES:
                    attr += ' TEXT'
                else:
                    attr += ' REAL'

                attributes_to_save.append(attr)

        sql = f"CREATE TABLE IF NOT EXISTS {rocket_part.__name__} (global_part_id INTEGER PRIMARY KEY, {', '.join(attributes_to_save)});"
        execute_sql(conn, sql)

        sql = f"""CREATE TABLE IF NOT EXISTS {rocket_part.__name__}_line (
                            global_part_id INTEGER,
                            rocket_id INTEGER,
                            location INTEGER,
                            FOREIGN KEY (global_part_id) REFERENCES {rocket_part.__name__}, 
                            FOREIGN KEY (rocket_id) REFERENCES Rocket (rocket_id),
                            PRIMARY KEY (global_part_id, rocket_id)
                );"""
        execute_sql(conn, sql)


def reset_db():
    try:
        conn = connect(DATABASE)

        sql = "DROP TABLE Rocket;"
        execute_sql(conn, sql)

        for rocket_part in ROCKET_PARTS:
            sql = f"DROP TABLE {rocket_part.__name__};"
            execute_sql(conn, sql)

            sql = f"DROP TABLE {rocket_part.__name__}_line;"
            execute_sql(conn, sql)
    except sqlite3.Error:
        pass
    
    init_db()


def save_rocket(rocket):
    conn = connect(DATABASE)

    sql = f"INSERT INTO Rocket (rocket_id, name) VALUES((SELECT MAX(rocket_id) FROM Rocket) + 1, '{rocket.name}')" # (SELECT MAX(rocket_id) FROM Rocket) + 1
    execute_sql(conn, sql)

    for index, part in enumerate(rocket.parts):
        part_data = []
        for key in vars(part).keys():
            if key not in BLACKLISTED_ATTRIBUTES:
                if key in TEXT_ATTRIBUTES:
                    part_data.append(f"'{vars(part)[key]}'")
                else:
                    part_data.append(str(("%.17f" % vars(part)[key]).rstrip('0').rstrip('.'))) # Convert scientific notation to decimal

        sql = f"INSERT INTO {part.__class__.__name__} VALUES((SELECT MAX(global_part_id) FROM {part.__class__.__name__}) + 1, {', '.join(part_data)})"
        execute_sql(conn, sql)

        sql = f"INSERT INTO {part.__class__.__name__}_line (global_part_id, rocket_id, location) VALUES((SELECT MAX(global_part_id) FROM {part.__class__.__name__}), (SELECT MAX(rocket_id) FROM Rocket), {index})"
        execute_sql(conn, sql)


def delete_rocket(rocket):
    conn = connect(DATABASE)

    sql = f"SELECT rocket_id FROM Rocket WHERE name = '{rocket.name}'"
    c = conn.cursor()
    c.execute(sql)
    rocket_id = c.fetchall()

    if len(rocket_id) > 0:
        rocket_id = rocket_id[0][0]
        sql = f"DELETE FROM Rocket WHERE name = '{rocket.name}'"
        execute_sql(conn, sql)

        for part in ROCKET_PARTS:
            sql = f"DELETE FROM {part.__name__} WHERE {part.__name__}.global_part_id = (SELECT {part.__name__}_line.global_part_id FROM {part.__name__}_line WHERE {part.__name__}_line.rocket_id = {rocket_id})"
            execute_sql(conn, sql)

            sql = f"DELETE FROM {part.__name__}_line WHERE rocket_id = {rocket_id}"
            execute_sql(conn, sql)


def get_rocket(name):
    conn = connect(DATABASE)

    column_names = []
    table_names = ["Rocket"]
    conditions = [f"Rocket.name = '{name}'"]
    for part in ROCKET_PARTS:
        table_names.append(part.__name__)
        table_names.append(part.__name__ + "_line")
        conditions.append(f"{part.__name__}.global_part_id = {part.__name__}_line.global_part_id")
        conditions.append(f"{part.__name__}_line.rocket_id = Rocket.rocket_id")
        column_names.append(f"{part.__name__}_line.location")
        for key in vars(part()).keys():
            if key not in BLACKLISTED_ATTRIBUTES:
                column_names.append(f"{part.__name__}.{key}")

    sql = f"SELECT {', '.join(column_names)} FROM {', '.join(table_names)} WHERE {' AND '.join(conditions)}"
    data = execute_sql(conn, sql)[0]

    data_dict = {}
    for i, column in enumerate(column_names):
        data_dict.update({column:data[i]})

    all_args = []
    for part in ROCKET_PARTS:
        args = {'part':part}
        for i, column in enumerate(column_names):
            if column.split('.')[0] == part.__name__ or column.split('.')[0] == part.__name__ + "_line":
                args.update({column.split('.')[1]:data[i]})

        all_args.append(args)

    rocket = Rocket(name=name)
    rocket.parts = [None] * len(all_args)

    for args in all_args:
        location = args.pop('location')
        part = args.pop('part')
        rocket.parts[location] = part(**args)
    
    for part in rocket.parts:
        if isinstance(part, Fins) or isinstance(part, Engine):
            print(part.parent)
    
    return rocket


def get_all_saved_rockets():
    conn = connect(DATABASE)

    sql = "SELECT name FROM Rocket"

    c = conn.cursor()
    c.execute(sql)
    names = c.fetchall()

    rockets = []
    for name in names:
        rockets.append(get_rocket(name[0]))
    
    return rockets


# reset_db()
# rocket = file_handler.get_all_saved_rockets()[0]
# rocket.name = rocket.name + " 2"
# save_rocket(rocket)
# get_rocket('New Rocket')

# delete_rocket("New Rocket")

# print(get_all_saved_rockets())