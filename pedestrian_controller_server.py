# pedestrian_controller.py
from xmlrpc.server import SimpleXMLRPCServer
import mysql.connector # ADDED

# --- ADDED: Database Configuration ---
db_config = {
    'host': 'localhost', 
    'user': 'root',
    'password': '',
    'database': 'pedestrian_db'
}

def pedestrian_controller(road_a_status, road_b_status):
    """
    Determines the state of pedestrian signals based on road traffic status.
    """
    print(f"\n[PEDESTRIAN] Received status: Road A -> {road_a_status}, Road B -> {road_b_status}")
    actions = []
    # (Logic for creating pedestrian actions is unchanged)
    if road_a_status == 'green':
        actions.append({'id': 'p1', 'status': 'red', 'delay': 0})
        actions.append({'id': 'p2', 'status': 'red', 'delay': 0})
    else:
        actions.append({'id': 'p1', 'status': 'green', 'delay': 0})
        actions.append({'id': 'p2', 'status': 'green', 'delay': 0})

    if road_b_status == 'green':
        actions.append({'id': 'p3', 'status': 'red', 'delay': 0})
        actions.append({'id': 'p4', 'status': 'red', 'delay': 0})
    else:
        actions.append({'id': 'p3', 'status': 'green', 'delay': 0})
        actions.append({'id': 'p4', 'status': 'green', 'delay': 0})
        
    print(f"[PEDESTRIAN] Returning {len(actions)} pedestrian actions.")
    return actions

# --- ADDED: Function to update its own database ---
def update_pedestrian_db(final_status_dict):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    update_query = "UPDATE signal_states SET current_status = %s WHERE signal_id = %s"
    
    for signal_id, status in final_status_dict.items():
        cursor.execute(update_query, (status, signal_id))
    
    conn.commit()
    conn.close()
    print("[PEDESTRIAN] Database has been updated.")
    return True # Return success


# (Server setup is modified to register the new function)
with SimpleXMLRPCServer(('0.0.0.0', 8002), logRequests=False, allow_none=True) as server:
    server.register_introspection_functions()
    print("Pedestrian Controller Server listening on port 8002...")
    server.register_function(pedestrian_controller)
    server.register_function(update_pedestrian_db) # Register new function
    server.serve_forever()