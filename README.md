# WireDesk - Custom Wire Configurator & Production Order Display

**WireDesk** is a Python-based desktop application built with **PyQt6**. It serves as a dynamic wire configuration tool designed to help manufacturers and engineers calculate wire specifications, estimate costs, check compliance against standards (IS 694), and manage production orders.

## 🚀 Features

* **Dynamic Form Generation:** The UI for every wire type is generated automatically from JSON configuration files. Adding a new wire type is as simple as creating a new JSON file.
* **Real-time Calculation Engine:** A custom engine parses mathematical formulas defined in JSON strings to calculate dimensions, weights (Copper/PVC), and costs instantly based on user input.
* **Standard Compliance Checks:** Automatically validates calculated dimensions and insulation thickness against **IS 694 Standards** using built-in lookup tables (Tables 3, 4, 5, 6, 7, 9, 10).
* **Order Management:** Saves valid configurations to an SQLite database (`orders.db`) for production tracking.
* **Analytics Tracking:** Logs cost and weight data into an analytics database (`analytics.db`) for dashboard reporting.
* **Modern UI:** Features a dark-themed interface using `qdarkstyle`, custom card widgets, and smooth accordion animations.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** PyQt6
* **Styling:** QDarkStyle, Custom CSS
* **Database:** SQLite3
* **Data Format:** JSON (for logic and configuration)

## 📂 Project Structure

    WireDesk/
    │
    ├── app.py                  # Main entry point. Sets up the Dashboard and Grid View.
    ├── overlay.py              # Handles the detailed configuration view, calculations, and DB saving.
    ├── calculation_engine.py   # Logic to parse JSON formulas and execute calculations safely.
    ├── json_form.py            # Generates UI input fields dynamically from JSON data.
    ├── accordion.py            # Custom collapsible widget implementation.
    ├── card_widget.py          # Custom widget for the wire selection cards.
    │
    ├── data/                   # JSON configuration files for different wire types
    │   ├── house_wire.json
    │   ├── multi_core_round_cable.json
    │   ├── service_wire.json
    │   └── ...
    │
    ├── lookup_table/           # Python dictionaries representing IS 694 Standard Tables
    │   ├── lookup_registry.py  # Registry to fetch specific table data dynamically.
    │   ├── lookup_table_3.py
    │   ├── lookup_table_4.py
    │   └── ...
    │
    ├── db/
    │   └── init_dbs.py         # Script to initialize/reset the SQLite databases.
    │
    ├── img/                    # Images for the dashboard cards
    └── README.md

## ⚙️ Installation & Setup

1. **Clone the Repository**

        git clone [https://github.com/yourusername/WireDesk.git](https://github.com/yourusername/WireDesk.git)
        cd WireDesk

2. **Install Dependencies**
   You will need Python installed. Install the required libraries:

        pip install PyQt6 QDarkStyle

3. **Initialize the Database**
   Before running the app for the first time, generate the SQLite databases:

        python db/init_dbs.py

   *This will create `orders.db` and `analytics.db` in your root directory.*

4. **Run the Application**

        python app.py

## 📖 How It Works

### 1. The Configuration System (JSON)
The core logic resides in the `data/` folder. Each JSON file defines:
* **Constants:** Base values like specific gravity of Copper/Aluminium/PVC.
* **Lookup Standard:** Defines which IS 694 table to use for validation.
* **User Input:** Defines which fields the user needs to type in (e.g., `length_meters`, `insulation_percent`).
* **Calculated:** Contains mathematical formulas stored as strings.
    * *Example:* `"conductor_area_sqmm": "pi * strand_diameter_mm**2 / 4 * number_of_strands"`
* **Compliance:** Python conditional strings to return "Yes" or "No" based on calculated values vs. lookup table limits.

### 2. The Calculation Engine
The `CalculationEngine` class loads the JSON, safely executes the string formulas using Python's `eval` (within a restricted scope), and updates the UI in real-time as the user types.

### 3. Database Saving
When the user clicks **Add**, the application checks:
1. Are all compliance checks "Yes"?
2. If passed, it saves the technical specs to `orders.db`.
3. It saves the cost/weight breakdown to `analytics.db`.

## 🤝 Contributing

Contributions are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

