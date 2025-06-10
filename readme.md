# Student Result Management System

This is a web-based application designed to manage student academic results. The system provides separate interfaces for students and administrators, allowing for secure access to result information.

## About The Project

The Student Result Management System is a comprehensive solution for educational institutions to manage and disseminate student results efficiently. It provides a centralized platform for administrators to add, update, and view student results, while students can log in to view their academic performance. The system is built with a focus on usability, security, and scalability.

### Key Features

#### Admin Features

* **Secure Admin Login:** Admins have a secure login to access their dashboard.
* **Admin Dashboard:** A comprehensive dashboard that provides an overview of all student results.
* **Result Management:**
    * **Add Results:** Admins can add new results for students, including detailed components such as paper scores and weights.
    * **Update Results:** Existing results can be easily updated.
    * **Delete Results:** Admins can delete result records.
* **View All Results:** View a complete list of all student results, with options to filter by IGCSE and A-Level.
* **Search and Filter:** Search for specific student results using filters for Student ID, Subject Name, Exam Level, and Session.

#### Student Features

* **Secure Student Login:** Students can log in to view their results securely.
* **Student Dashboard:** A personalized dashboard that welcomes the student.
* **View Results:** Students can view their own academic results.
* **Filter Results:** Students can filter their results by Subject Name, Exam Level, and Session to easily find the information they need.

### Upcoming Features

* **User Registration:** A registration system for new students and admins.
* **Profile Management:** Users can manage their own profiles.
* **Graphical Analysis:** Visual representation of results using charts and graphs to track performance over time.
* **Export to PDF/CSV:** The ability to export results to PDF or CSV files.
* **Email Notifications:** Automated email notifications to students when new results are published.
* **Advanced Search:** More advanced search and filtering capabilities.
* **API Endpoints:** A RESTful API for integration with other systems.

## Technologies Used

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, JavaScript
* **Database:** MySQL
* **Python Libraries:**
    * Flask
    * mysql-connector-python
    * Werkzeug
    * Jinja2
    * and other dependencies listed in `requirements.txt`.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.x
* MySQL Server
* pip (Python package installer)

### Installation

1.  **Clone the repo**
    ```sh
    git clone [https://github.com/your_username/student-result-system.git](https://github.com/your_username/student-result-system.git)
    cd student-result-system
    ```
2.  **Create a virtual environment**
    ```sh
    python -m venv venv
    ```
3.  **Activate the virtual environment**
    * On Windows:
        ```sh
        venv\Scripts\activate
        ```
    * On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
4.  **Install Python packages**
    ```sh
    pip install -r requirements.txt
    ```
5.  **Set up the database**
    * Make sure your MySQL server is running.
    * Create a database named `StudentRecordSystem`.
    * You will need to create the necessary tables. You can infer the schema from the SQL queries in `app.py`.
6.  **Configure the application**
    * Open `app.py` and update the database configuration with your MySQL credentials:
        ```python
        db_config = {
            'host': 'localhost',
            'user': 'your_mysql_user',
            'password': 'your_mysql_password',
            'database': 'StudentRecordSystem'
        }
        ```
7.  **Run the application**
    ```sh
    python app.py
    ```
    The application will be running at `http://127.0.0.1:5001`.

## Usage

* **Admin Login:** Use admin credentials to log in. You will be redirected to the admin dashboard where you can manage student results.
* **Student Login:** Use student credentials to log in. You will be redirected to the student dashboard where you can view your results.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.