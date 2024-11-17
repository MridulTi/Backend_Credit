## Project Name: **Backend Dockerized Web Application**

### **Description**
This project is a web application built with [Your Framework/Language] and uses PostgreSQL as its database. The app is containerized using Docker for easy setup and deployment.

---

```markdown
### **Endpoints**
| Endpoint                            | HTTP Method | Description                                          |
|-------------------------------------|-------------|------------------------------------------------------|
| `/api/customer`                     | GET         | Fetches all customers                                |
| `/api/loan`                         | GET         | Fetches all loans                                    |
| `/api/customer/register`            | POST        | Registers a new customer                             |
| `/api/loan/create_loan`             | POST        | Creates a new loan                                   |
| `/api/loan/check_eligibility`       | POST        | Checks loan eligibility for a customer               |
| `/api/loan/view_loan_by_customer_id`| GET         | Fetches loans associated with a specific customer ID |
| `/api/loan/view_loan_by_loan_id`    | GET         | Fetches details of a specific loan by loan ID        |

```
### Demo Video

https://github.com/user-attachments/assets/4d22fe2d-59ac-40b6-a5c6-30aa2717e7ff

---

### **How to Run the Project**

#### **Using Docker**
1. **Install Docker:**  
   Ensure Docker is installed on your system. Download it from [Docker's official website](https://www.docker.com/).

2. **Build the Docker Image:**  
   Run the following command in the project directory:
   ```bash
   docker-compose up --build
   ```
   This will build the Docker image and start the application.

3. **Access the Application:**  
   Open your browser and go to `http://127.0.0.1:8000`.

4. **Stop the Application:**  
   Use the following command to stop the application:
   ```bash
   docker-compose down
   ```

---

#### **Running Without Docker**
1. **Install Dependencies:**
   - Install [Python](https://www.python.org/) and [PostgreSQL](https://www.postgresql.org/).
   - Install project dependencies using pip:
     ```bash
     pip install -r requirements.txt
     ```

2. **Set Up the Database:**
   - Create a PostgreSQL database.
   - Update the database credentials in the project configuration file (`settings.py` or `.env`).

3. **Run Database Migrations:**
   Apply migrations to set up the database schema:
   ```bash
   python manage.py migrate
   ```

4. **Start the Application:**
   Run the application:
   ```bash
   python manage.py process_tasks
   python manage.py runserver
   ```
   The app will be available at `http://127.0.0.1:8000`.

5. **Stop the Application:**  
   Press `Ctrl+C` in the terminal running the app.

---

### **Directory Structure**
```
.
├── Dockerfile
├── docker-compose.yml
├── app/
│   ├── entrypoint.sh
│   ├── manage.py
│   ├── requirements.txt
│   ├── [application files...]
└── README.md
```

---

### **Additional Notes**
- Ensure that the PostgreSQL service is running if not using Docker.
- For any issues, consult the project documentation or reach out to the maintainer.
