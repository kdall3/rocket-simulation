import sqlite3

from rocket_parts import *

DATABASE = 'rockets.db'
BLACKLISTED_ATTRIBUTES = ['being_dragged', 'selected', 'mass_override', 'hit_box', 'unrotated_hit_box', 'vertices', 'colour', 'parent']
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

    sql = """CREATE TABLE IF NOT EXISTS Stages (
            rocket_id INTEGER, 
            stage INTEGER, 
            local_part_id INTEGER,
            FOREIGN KEY (rocket_id) REFERENCES Rocket (rocket_id),
            PRIMARY KEY (rocket_id, stage, local_part_id)
        );"""
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

    # Check if rocket already exists

    sql = f"SELECT name FROM Rocket WHERE Rocket.name = '{rocket.name}'"
    existing_rockets = execute_sql(conn, sql)

    if len(existing_rockets) > 0:
        delete_rocket(Rocket(name=rocket.name))

    sql = f"INSERT INTO Rocket (rocket_id, name) VALUES((SELECT MAX(rocket_id) FROM Rocket) + 1, '{rocket.name}')"
    execute_sql(conn, sql)

    for stage_number, stage in enumerate(rocket.stages):
        for part_id in stage:
            sql = f"INSERT INTO Stages (rocket_id, stage, local_part_id) VALUES((SELECT MAX(rocket_id) FROM Rocket), {stage_number}, {part_id})"
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

        sql = f"DELETE FROM Stages WHERE rocket_id = {rocket_id}"
        execute_sql(conn, sql)

        for part in ROCKET_PARTS:
            sql = f"DELETE FROM {part.__name__} WHERE {part.__name__}.global_part_id = (SELECT {part.__name__}_line.global_part_id FROM {part.__name__}_line WHERE {part.__name__}_line.rocket_id = {rocket_id})"
            execute_sql(conn, sql)

            sql = f"DELETE FROM {part.__name__}_line WHERE rocket_id = {rocket_id}"
            execute_sql(conn, sql)


def get_rocket(name):
    conn = connect(DATABASE)

    # ROCKET

    rocket = Rocket(name=name)

    # PARTS

    all_args = []

    # Construct an SQL statement for each part type to get all instances of that part type in the database
    for part in ROCKET_PARTS:
        column_names = []
        table_names = ["Rocket"]
        conditions = [f"Rocket.name = '{name}'"]
    
        table_names.append(part.__name__)
        table_names.append(part.__name__ + "_line")
        conditions.append(f"{part.__name__}.global_part_id = {part.__name__}_line.global_part_id")
        conditions.append(f"{part.__name__}_line.rocket_id = Rocket.rocket_id")
        column_names.append(f"{part.__name__}_line.location")
        for key in vars(part()).keys():  # Get variables from part class
            if key not in BLACKLISTED_ATTRIBUTES:
                column_names.append(f"{part.__name__}.{key}")

        sql = f"SELECT DISTINCT {', '.join(column_names)} FROM {', '.join(table_names)} WHERE {' AND '.join(conditions)}"
        part_data = execute_sql(conn, sql)
        part_data = [list(data) for data in part_data]

        if len(part_data) > 0:  # Check if there are no parts of that type
            for individual_part_data in part_data: # Iterate through each instance of a part type
                args = {'part':part}
                for i, column_name in enumerate(column_names):
                    if column_name.split('.')[0] == part.__name__ or column_name.split('.')[0] == part.__name__ + '_line':
                        args.update({column_name.split('.')[1]:individual_part_data[i]}) # dictionary of part params with their values
            
                all_args.append(args)
    
    rocket.parts = [None] * len(all_args)

    for part in ROCKET_PARTS:
        column_names = []

    for args in all_args:
        location = args.pop('location')
        part = args.pop('part')
        rocket.parts[location] = part(**args)
    
    # STAGES

    sql = f"SELECT stage, local_part_id FROM Stages, Rocket WHERE Rocket.rocket_id = Stages.rocket_id AND Rocket.name = '{name}'"
    stages_data = execute_sql(conn, sql)
    stages_data = [list(stage) for stage in stages_data]
    max_stage = max([stage[0] for stage in stages_data])
    rocket.stages = [[] for _ in range(max_stage+1)]
    for stage in stages_data:  # DOESNT WORK, IDS GET ADDED TO EVERY STAGE FOR SOME REASON
        stage_num = stage[0]
        part_id = stage[1]
        rocket.stages[stage_num].append(part_id)
    
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
