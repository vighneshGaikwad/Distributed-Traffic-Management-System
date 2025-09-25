# 🚦 Distributed Traffic Control System

This project is a web-based simulation of a multi-service traffic signal control system. It demonstrates a microservice-style architecture where a central controller orchestrates separate services for traffic signal manipulation and pedestrian signals. The frontend provides a real-time visualization and control panel, communicating with the backend via SSE (Server-Sent Events).

The system is designed to run in a continuous, automatic loop but also features a manual override for emergency scenarios and the ability to pause/resume the automation.



---

## ✨ Features

* **Real-Time Visualization**: A clean web interface shows the status of 4 vehicle signals and 4 pedestrian signals.
* **Microservice Architecture**: The system is split into three distinct services that communicate via XML-RPC:
    1.  **Controller Service**: The main brain, orchestrating all actions.
    2.  **Manipulator Service**: Manages the state of vehicle signals.
    3.  **Pedestrian Service**: Manages the state of pedestrian signals.
* **Automatic Control Loop**: Once started, the system automatically cycles through traffic patterns based on a random timer.
* **Toggle Automation**: A dedicated UI button allows you to **start and stop** the automatic control loop at any time.
* **Manual Emergency Override**: Instantly interrupt the automatic cycle to force a specific road to have a green light for a fixed duration before reverting to its previous state.
* **Database Persistence**: Signal states are saved in three separate MySQL databases, one for each service, ensuring state consistency.
* **Live Event Log**: See a stream of events directly from the backend, including automatic decisions, countdowns, and override alerts.

---

## 🛠️ Tech Stack

* **Backend**: Python
    * **Web Server & API**: Flask
    * **Service Communication**: XML-RPC
* **Database**: MySQL
* **Frontend**: HTML, Tailwind CSS, JavaScript (via CDN)

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

* **Python 3.x**: Make sure Python is installed and accessible from your command line.
* **Pip**: Python's package installer (usually comes with Python).
* **MySQL Server**: A running MySQL database instance. **XAMPP** or **WAMP** are excellent choices as they provide Apache and phpMyAdmin.
* **Git**: For cloning the repository.

### 1. Clone the Repository

Open your terminal or command prompt and run the following command:
```bash
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name
```

### 2. Install Python Dependencies

Install the required Python libraries using pip.
```bash
pip install Flask mysql-connector-python
```

### 3. Set Up the Databases

This is a critical step. The project requires **three separate databases**.

1.  Start your MySQL server (e.g., by starting Apache and MySQL in the XAMPP control panel).
2.  Navigate to your database management tool (e.g., `http://localhost/phpmyadmin`).
3.  Create three new, empty databases with the following names:
    * `controller_db`
    * `manipulator_db`
    * `pedestrian_db`

4.  Execute the following SQL script **in each of the three databases**. This will create the necessary table and populate it with the initial signal states.

    ```sql
    --
    -- Table structure for table `signal_states`
    --
    CREATE TABLE `signal_states` (
      `signal_id` varchar(10) NOT NULL,
      `current_status` varchar(10) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    --
    -- Dumping data for table `signal_states`
    --
    INSERT INTO `signal_states` (`signal_id`, `current_status`) VALUES
    ('1', 'red'),
    ('2', 'red'),
    ('3', 'green'),
    ('4', 'green'),
    ('p1', 'green'),
    ('p2', 'green'),
    ('p3', 'red'),
    ('p4', 'red');

    --
    -- Indexes for table `signal_states`
    --
    ALTER TABLE `signal_states`
      ADD PRIMARY KEY (`signal_id`);
    ```

### 4. Running the Application

A batch file is included to make launching the system easy.

1.  Simply **double-click the `run_servers.bat` file**.
2.  This will automatically open three separate terminal windows, one for each Python service. You will see output indicating that each server is listening on its respective port (5000, 8001, 8002).
3.  Open your web browser and navigate to:
    **`http://127.0.0.1:5000`**

### 5. How to Use the System

* **Start Automation**: Click the "Start Automation" button to begin the automatic signal cycling. The button will change to "Stop Automation".
* **Stop Automation**: Click the "Stop Automation" button to pause the automatic cycle after the current countdown finishes.
* **Manual Override**:
    * Enter a signal number (1-4) into the input field.
    * Click the "Override" button.
    * The system will immediately change the lights to give that road a green signal for 7 seconds before reverting and resuming the automatic cycle.

Enjoy the simulation!
