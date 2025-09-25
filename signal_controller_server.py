# # signal_controller_server.py
# from flask import Flask, render_template, jsonify, Response, request # MODIFIED: Added 'request'
# import xmlrpc.client
# import json
# import time
# import random
# from queue import Queue
# from threading import Lock
# import mysql.connector

# app = Flask(__name__)
# sse_queue = Queue()
# CONTROLLER_LOCK = Lock()

# MANIPULATOR_URL = "http://localhost:8001"
# PEDESTRIAN_URL = "http://localhost:8002"

# # Database Configuration (unchanged)
# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '',
#     'database': 'controller_db'
# }

# # --- Helper and Core Logic Functions (unchanged) ---

# def push_sse_message(data):
#     sse_queue.put(f"data: {json.dumps(data)}\n\n")

# def update_controller_db(final_status_dict):
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()
#     update_query = "UPDATE signal_states SET current_status = %s WHERE signal_id = %s"
#     for signal_id, status in final_status_dict.items():
#         cursor.execute(update_query, (status, signal_id))
#     conn.commit()
#     conn.close()
#     print("[CONTROLLER] Database has been updated.")

# def signal_controller():
#     print("\n[CONTROLLER] Triggered. Making a decision...")
#     push_sse_message({"type": "log", "message": "------------------------------------------"})
#     push_sse_message({"type": "log", "message": "[CONTROLLER] Making a decision..."})

#     manipulator_server = xmlrpc.client.ServerProxy(MANIPULATOR_URL)
#     pedestrian_server = xmlrpc.client.ServerProxy(PEDESTRIAN_URL)
    
#     current_status = manipulator_server.get_initial_status()
#     final_state = current_status.copy()
#     random_choice = random.randint(1, 4)
#     print(f"[CONTROLLER] Random choice: {random_choice}. Current status of signal 1: {current_status['1']}")

#     actions = []
    
#     # Case 1: Change Road A to Green
#     if random_choice in [1, 2] and current_status['1'] == 'red':
#         print("[CONTROLLER] Decision: Road A -> GREEN.")
#         actions = manipulator_server.signal_manipulator([3, 4], [1, 2])
#         pedestrian_actions = pedestrian_server.pedestrian_controller('green', 'red')
#         final_state.update({'1':'green', '2':'green', '3':'red', '4':'red', 'p1':'red', 'p2':'red', 'p3':'green', 'p4':'green'})

#     # Case 2: Change Road B to Green
#     elif random_choice in [3, 4] and current_status['3'] == 'red':
#         print("[CONTROLLER] Decision: Road B -> GREEN.")
#         actions = manipulator_server.signal_manipulator([1, 2], [3, 4])
#         pedestrian_actions = pedestrian_server.pedestrian_controller('red', 'green')
#         final_state.update({'1':'red', '2':'red', '3':'green', '4':'green', 'p1':'green', 'p2':'green', 'p3':'red', 'p4':'red'})
#     else:
#         print("[CONTROLLER] Decision: No state change required.")
#         push_sse_message({"type": "log", "message": "[CONTROLLER] Decision: No state change required."})
    
#     if actions:
#         actions[2].update({'pedestrian_actions': pedestrian_actions})
        
#     return actions, final_state


# # --- Flask Web Server Routes ---
# # (/, /api/status, /stream routes are unchanged)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/api/status')
# def get_status():
#     try:
#         manipulator_server = xmlrpc.client.ServerProxy(MANIPULATOR_URL)
#         return jsonify(manipulator_server.get_initial_status())
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/stream')
# def stream():
#     def event_stream():
#         while True:
#             message = sse_queue.get()
#             yield message
#     return Response(event_stream(), mimetype='text/event-stream')

# # (/api/control route is unchanged)
# @app.route('/api/control', methods=['POST'])
# def control_signal_route():
#     if not CONTROLLER_LOCK.acquire(blocking=False):
#         return jsonify({"error": "Signal change already in progress. Please wait."}), 409

#     try:
#         push_sse_message({"type": "control", "action": "disable_button"})
#         actions, final_state = signal_controller()

#         if actions:
#             for action in actions:
#                 time.sleep(action['delay'])
#                 push_sse_message({"type": "update", "id": action['id'], "status": action['status']})
#                 if 'pedestrian_actions' in action:
#                     for p_action in action['pedestrian_actions']:
#                         push_sse_message({"type": "update", "id": p_action['id'], "status": p_action['status']})

#         push_sse_message({"type": "log", "message": "--- Sequence Complete ---"})
        
#         if actions: 
#             push_sse_message({"type": "log", "message": "[CONTROLLER] Orchestrating database updates..."})
#             manipulator_server = xmlrpc.client.ServerProxy(MANIPULATOR_URL)
#             pedestrian_server = xmlrpc.client.ServerProxy(PEDESTRIAN_URL)

#             print(f"[CONTROLLER] Final state to be saved: {final_state}")

#             update_controller_db(final_state)
#             pedestrian_server.update_pedestrian_db(final_state)
#             manipulator_server.update_manipulator_db(final_state)
            
#             push_sse_message({"type": "log", "message": "[CONTROLLER] All databases updated."})
            
#         push_sse_message({"type": "control", "action": "enable_button"})
#         return jsonify(success=True)

#     except Exception as e:
#         error_msg = f"[ERROR] An error occurred: {e}"
#         print(error_msg)
#         push_sse_message({"type": "log", "message": error_msg})
#         push_sse_message({"type": "control", "action": "enable_button"})
#         return jsonify({"error": str(e)}), 500
        
#     finally:
#         CONTROLLER_LOCK.release()
#         print("[SERVER] Lock has been released.")

# # --- ADDED: New route for manual override ---
# @app.route('/api/override', methods=['POST'])
# def manual_override_route():
#     if not CONTROLLER_LOCK.acquire(blocking=False):
#         return jsonify({"error": "System busy with another operation. Please wait."}), 409

#     try:
#         data = request.get_json()
#         target_signal_id = str(data.get('signal_id'))
#         if not target_signal_id in ['1', '2', '3', '4']:
#              return jsonify({"error": "Invalid signal ID provided."}), 400

#         push_sse_message({"type": "control", "action": "disable_button"})
#         push_sse_message({"type": "log", "message": f"--- MANUAL OVERRIDE for Signal {target_signal_id} ---"})

#         manipulator_server = xmlrpc.client.ServerProxy(MANIPULATOR_URL)
#         pedestrian_server = xmlrpc.client.ServerProxy(PEDESTRIAN_URL)
        
#         # 1. Store the state before the override
#         pre_override_state = manipulator_server.get_initial_status()
#         print(f"[OVERRIDE] State before override: {pre_override_state}")

#         # 2. Determine and execute the override actions
#         override_actions = []
#         if target_signal_id in ['3', '4'] and pre_override_state.get('3') == 'red':
#             push_sse_message({"type": "log", "message": "[OVERRIDE] Forcing Road B to GREEN."})
#             override_actions = manipulator_server.signal_manipulator([1, 2], [3, 4])
#             ped_actions = pedestrian_server.pedestrian_controller('red', 'green')
#             override_actions[2].update({'pedestrian_actions': ped_actions})
#         elif target_signal_id in ['1', '2'] and pre_override_state.get('1') == 'red':
#             push_sse_message({"type": "log", "message": "[OVERRIDE] Forcing Road A to GREEN."})
#             override_actions = manipulator_server.signal_manipulator([3, 4], [1, 2])
#             ped_actions = pedestrian_server.pedestrian_controller('green', 'red')
#             override_actions[2].update({'pedestrian_actions': ped_actions})
        
#         if not override_actions:
#             push_sse_message({"type": "log", "message": "[OVERRIDE] Target road is already green. No action taken."})
#         else:
#             # Execute the change sequence via SSE
#             for action in override_actions:
#                 time.sleep(action['delay'])
#                 push_sse_message({"type": "update", "id": action['id'], "status": action['status']})
#                 if 'pedestrian_actions' in action:
#                     for p_action in action['pedestrian_actions']:
#                         push_sse_message({"type": "update", "id": p_action['id'], "status": p_action['status']})
            
#             # 3. Wait for the specified duration
#             push_sse_message({"type": "log", "message": "[OVERRIDE] State active. Reverting in 7 seconds..."})
#             time.sleep(7)
#             push_sse_message({"type": "log", "message": "[OVERRIDE] Reverting to pre-override state."})

#             # 4. Determine and execute reversion actions
#             revert_actions = []
#             if pre_override_state.get('1') == 'green': # Original state was Road A Green
#                  revert_actions = manipulator_server.signal_manipulator([3, 4], [1, 2])
#                  ped_actions = pedestrian_server.pedestrian_controller('green', 'red')
#                  revert_actions[2].update({'pedestrian_actions': ped_actions})
#             else: # Original state was Road B Green
#                  revert_actions = manipulator_server.signal_manipulator([1, 2], [3, 4])
#                  ped_actions = pedestrian_server.pedestrian_controller('red', 'green')
#                  revert_actions[2].update({'pedestrian_actions': ped_actions})

#             for action in revert_actions:
#                 time.sleep(action['delay'])
#                 push_sse_message({"type": "update", "id": action['id'], "status": action['status']})
#                 if 'pedestrian_actions' in action:
#                     for p_action in action['pedestrian_actions']:
#                         push_sse_message({"type": "update", "id": p_action['id'], "status": p_action['status']})

#         push_sse_message({"type": "log", "message": "--- OVERRIDE COMPLETE ---"})
#         return jsonify(success=True)

#     finally:
#         push_sse_message({"type": "control", "action": "enable_button"})
#         CONTROLLER_LOCK.release()
#         print("[SERVER] Override Lock has been released.")


# if __name__ == '__main__':
#     print("Starting Flask Web Server...")
#     app.run(host='0.0.0.0', port=5000)

# signal_controller_server.py
from flask import Flask, render_template, jsonify, Response, request
import xmlrpc.client
import json
import time
import random
from queue import Queue
from threading import Lock, Thread, Event
import mysql.connector

app = Flask(__name__)
sse_queue = Queue()

# --- MODIFIED: System Control Variables ---
CONTROLLER_LOCK = Lock()       # Global lock for all signal-changing operations
automation_thread = None       # To hold the background thread object
stop_automation_event = Event() # Event to signal the automation loop to stop/pause

MANIPULATOR_URL = "http://localhost:8001"
PEDESTRIAN_URL = "http://localhost:8002"

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'controller_db'
}

# --- Helper and Core Logic Functions ---

def push_sse_message(data):
    """Puts a message onto the SSE queue for the frontend."""
    sse_queue.put(f"data: {json.dumps(data)}\n\n")

def update_controller_db(final_status_dict):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    update_query = "UPDATE signal_states SET current_status = %s WHERE signal_id = %s"
    for signal_id, status in final_status_dict.items():
        cursor.execute(update_query, (status, signal_id))
    conn.commit()
    conn.close()
    print("[CONTROLLER] Database has been updated.")

def signal_controller():
    """Decides on the next signal change based on a random number."""
    # This function's internal logic is unchanged.
    print("\n[CONTROLLER] Making an automatic decision...")
    push_sse_message({"type": "log", "message": "------------------------------------------"})
    push_sse_message({"type": "log", "message": "[CONTROLLER] Making a decision..."})
    manipulator_server = xmlrpc.client.ServerProxy(MANIPULATOR_URL)
    current_status = manipulator_server.get_initial_status()
    final_state = current_status.copy()
    random_choice = random.randint(1, 4)
    print(f"[CONTROLLER] Random choice: {random_choice}")
    push_sse_message({"type": "log", "message": f"[CONTROLLER] Generated random choice: {random_choice}"})
    actions = []
    if random_choice in [1, 2] and current_status['1'] == 'red':
        actions = manipulator_server.signal_manipulator([3, 4], [1, 2])
        pedestrian_actions = xmlrpc.client.ServerProxy(PEDESTRIAN_URL).pedestrian_controller('green', 'red')
        final_state.update({'1':'green', '2':'green', '3':'red', '4':'red', 'p1':'red', 'p2':'red', 'p3':'green', 'p4':'green'})
    elif random_choice in [3, 4] and current_status['3'] == 'red':
        actions = manipulator_server.signal_manipulator([1, 2], [3, 4])
        pedestrian_actions = xmlrpc.client.ServerProxy(PEDESTRIAN_URL).pedestrian_controller('red', 'green')
        final_state.update({'1':'red', '2':'red', '3':'green', '4':'green', 'p1':'green', 'p2':'green', 'p3':'red', 'p4':'red'})
    else:
        push_sse_message({"type": "log", "message": "[CONTROLLER] Decision: No state change required."})
    if actions:
        actions[2].update({'pedestrian_actions': pedestrian_actions})
    return actions, final_state

def execute_actions(actions):
    """Pushes a sequence of signal changes to the UI via SSE."""
    for action in actions:
        time.sleep(action['delay'])
        push_sse_message({"type": "update", "id": action['id'], "status": action['status']})
        if 'pedestrian_actions' in action:
            for p_action in action['pedestrian_actions']:
                push_sse_message({"type": "update", "id": p_action['id'], "status": p_action['status']})

def control_loop():
    """This function runs in a background thread and controls the signals automatically."""
    while not stop_automation_event.is_set():
        with CONTROLLER_LOCK:
            try:
                actions, final_state = signal_controller()
                if actions:
                    execute_actions(actions)
                    # Database updates
                    push_sse_message({"type": "log", "message": "[CONTROLLER] Orchestrating database updates..."})
                    manipulator_server = xmlrpc.client.ServerProxy(MANIPULATOR_URL)
                    pedestrian_server = xmlrpc.client.ServerProxy(PEDESTRIAN_URL)
                    update_controller_db(final_state)
                    pedestrian_server.update_pedestrian_db(final_state)
                    manipulator_server.update_manipulator_db(final_state)
                    push_sse_message({"type": "log", "message": "[CONTROLLER] All databases updated."})
                push_sse_message({"type": "log", "message": "--- Sequence Complete ---"})
            except Exception as e:
                error_msg = f"[ERROR] Control loop failed: {e}"
                print(error_msg)
                push_sse_message({"type": "log", "message": error_msg})

        # Countdown for the next cycle, can be interrupted by stop_automation_event
        countdown_duration = 8
        for i in range(countdown_duration, 0, -1):
            if stop_automation_event.is_set():
                break
            push_sse_message({"type": "log", "message": f"Next change in {i}..."})
            time.sleep(1)

# --- Flask Web Server Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    try:
        return jsonify(xmlrpc.client.ServerProxy(MANIPULATOR_URL).get_initial_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            yield sse_queue.get()
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/api/toggle_automation', methods=['POST'])
def toggle_automation():
    """Starts or stops the automatic control loop."""
    global automation_thread
    if stop_automation_event.is_set(): # If it's stopped, start it
        stop_automation_event.clear()
        if not automation_thread or not automation_thread.is_alive():
            automation_thread = Thread(target=control_loop, daemon=True)
            automation_thread.start()
        push_sse_message({"type": "automation_status", "status": "running"})
        return jsonify(message="Automation started.", status="running")
    else: # If it's running, stop it
        stop_automation_event.set()
        push_sse_message({"type": "automation_status", "status": "stopped"})
        return jsonify(message="Automation stopped.", status="stopped")

@app.route('/api/override', methods=['POST'])
def manual_override_route():
    """Interrupts the cycle to manually change signals, then reverts."""
    with CONTROLLER_LOCK:
        data = request.get_json()
        target_signal_id = str(data.get('signal_id'))
        if not target_signal_id in ['1', '2', '3', '4']:
            return jsonify({"error": "Invalid signal ID."}), 400

        push_sse_message({"type": "control", "action": "disable_buttons"})
        push_sse_message({"type": "log", "message": f"--- MANUAL OVERRIDE for Signal {target_signal_id} ---"})
        
        manipulator_server = xmlrpc.client.ServerProxy(MANIPULATOR_URL)
        pedestrian_server = xmlrpc.client.ServerProxy(PEDESTRIAN_URL)
        
        pre_override_state = manipulator_server.get_initial_status()
        
        override_actions, revert_actions = [], []
        
        # Determine override and revert actions
        if target_signal_id in ['1', '2'] and pre_override_state.get('1') == 'red':
            override_actions = manipulator_server.signal_manipulator([3, 4], [1, 2])
            override_actions[2].update({'pedestrian_actions': pedestrian_server.pedestrian_controller('green', 'red')})
        elif target_signal_id in ['3', '4'] and pre_override_state.get('3') == 'red':
            override_actions = manipulator_server.signal_manipulator([1, 2], [3, 4])
            override_actions[2].update({'pedestrian_actions': pedestrian_server.pedestrian_controller('red', 'green')})

        if not override_actions:
            push_sse_message({"type": "log", "message": "[OVERRIDE] Target road already green. No action taken."})
        else:
            execute_actions(override_actions)
            push_sse_message({"type": "log", "message": "[OVERRIDE] State active. Reverting in 7 seconds..."})
            time.sleep(7)
            
            # Revert logic
            push_sse_message({"type": "log", "message": "[OVERRIDE] Reverting to pre-override state."})
            if pre_override_state.get('1') == 'green':
                revert_actions = manipulator_server.signal_manipulator([3, 4], [1, 2])
                revert_actions[2].update({'pedestrian_actions': pedestrian_server.pedestrian_controller('green', 'red')})
            else: # Original state was Road B Green
                revert_actions = manipulator_server.signal_manipulator([1, 2], [3, 4])
                revert_actions[2].update({'pedestrian_actions': pedestrian_server.pedestrian_controller('red', 'green')})
            execute_actions(revert_actions)

            # Sync DB with the final, reverted state
            update_controller_db(pre_override_state)
            pedestrian_server.update_pedestrian_db(pre_override_state)
            manipulator_server.update_manipulator_db(pre_override_state)

        push_sse_message({"type": "log", "message": "--- OVERRIDE COMPLETE ---"})
        push_sse_message({"type": "control", "action": "enable_buttons"})
        return jsonify(success=True)

if __name__ == '__main__':
    stop_automation_event.set() # Start in a stopped state
    app.run(host='0.0.0.0', port=5000)