# signal_manipulator_server.py
from xmlrpc.server import SimpleXMLRPCServer
import mysql.connector

# --- Database Configuration ---
db_config = {
    'host': 'localhost', 
    'user': 'root',
    'password': '',
    'database': 'manipulator_db'
}

def get_status_from_db():
    """Fetches the current signal states from the database."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT signal_id, current_status FROM signal_states")
    rows = cursor.fetchall()
    conn.close()
    return {row['signal_id']: row['current_status'] for row in rows}

# MODIFIED: Renamed function for clarity and it will now be called by the controller
def update_manipulator_db(status_dict):
    """Updates the database with the provided status dictionary."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    update_query = "UPDATE signal_states SET current_status = %s WHERE signal_id = %s"
    
    for signal_id, status in status_dict.items():
        cursor.execute(update_query, (status, signal_id))
    
    conn.commit()
    conn.close()
    print("[MANIPULATOR] Database has been updated by controller's command.")
    return True # Return success

def signal_manipulator(to_red_ids, to_green_ids):
    """
    This function now ONLY calculates the sequence of actions.
    It no longer updates the database itself.
    """
    print(f"\n[MANIPULATOR] Received command: RED->{to_red_ids}, GREEN->{to_green_ids}")
    actions = []
    
    # Logic for creating actions remains the same
    for signal_id in to_red_ids:
        actions.append({'id': signal_id, 'status': 'yellow', 'delay': 0})
    
    is_first_action_after_delay = True
    for signal_id in to_red_ids:
        delay = 5 if is_first_action_after_delay else 0
        actions.append({'id': signal_id, 'status': 'red', 'delay': delay})
        is_first_action_after_delay = False 

    for signal_id in to_green_ids:
        delay = 5 if is_first_action_after_delay else 0
        actions.append({'id': signal_id, 'status': 'green', 'delay': delay})
        is_first_action_after_delay = False
    
    # REMOVED: The database update call is no longer here.
    # update_db_from_dict(current_signal_status)

    print(f"[MANIPULATOR] Returning {len(actions)} transition actions.")
    return actions

def get_initial_status():
    print("[MANIPULATOR] Controller requested initial status from DB.")
    return get_status_from_db()

# --- MODIFIED: Server setup registers the new update function ---
with SimpleXMLRPCServer(('0.0.0.0', 8001), logRequests=False, allow_none=True) as server:
    server.register_introspection_functions()
    print("Signal Manipulator Server listening on port 8001...")
    server.register_function(signal_manipulator)
    server.register_function(get_initial_status)
    server.register_function(update_manipulator_db) # ADDED
    server.serve_forever()