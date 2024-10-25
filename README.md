
# **Planetarium**

**Planetarium** is a web application for managing a planetarium, allowing users to view and book shows, access information on various topics, and manage screening sessions. The application features user authentication, content management, and administrative functionalities.

## **Table of Contents**

- [Technologies](#technologies)
- [Installation and Setup](#installation-and-setup)
- [Using Docker](#using-docker)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Using the Application](#using-the-application)
- [Authorization and Authentication](#authorization-and-authentication)

## **Technologies**

- **Django** - the main web framework.
- **Django REST Framework** - used for building the API.
- **PostgreSQL** - the relational database for data storage.
- **Django JWT** - for user authentication using JSON Web Tokens.
- **Pillow** - for image handling.

## **Installation and Setup**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/planetarium.git
   cd planetarium
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # For Windows
   venv\Scripts\activate
   # For MacOS/Linux
   source venv/bin/activate
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Ensure PostgreSQL is running.
   - Create a new database for the project.
   - Update the `DATABASES` setting in `settings.py` with your database credentials.

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server:**
   ```bash
   python manage.py runserver
   ```

## **Using Docker**

If you prefer to use Docker for setting up the project, follow these steps:

1. **Ensure Docker and Docker Compose are installed.**

2. **Build and run the containers:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application at:**
   ```
   http://localhost:8000
   ```

4. **Run migrations within the Docker container (if needed):**
   ```bash
   docker-compose exec app python manage.py migrate
   ```

5. **Create a superuser in the Docker container (optional):**
   ```bash
   docker-compose exec app python manage.py createsuperuser
   ```

## **Running Tests**

To run the test suite, use the following command:

```bash
python manage.py test
```

You can also run tests within the Docker container:

```bash
docker-compose exec app python manage.py test
```

## **API Documentation**

The Planetarium API provides endpoints for managing shows, users, and sessions. Below are some key endpoints:

- **User Registration:** `POST /api/user/register/`
- **Token Obtain:** `POST /api/user/token/`
- **Token Refresh:** `POST /api/user/token/refresh/`
- **Get Current User:** `GET /api/user/me/`

Refer to the API documentation in the project for detailed information about each endpoint.

## **Using the Application**

- Visit `http://localhost:8000` to access the application.
- You can register as a user and log in to book shows and view details.
- Admin users can manage shows, sessions, and other content via the admin panel.

## **Authorization and Authentication**

This application uses JWT (JSON Web Tokens) for user authentication. Users must log in to access certain features. After successful login, users will receive a token that must be included in the headers of subsequent requests:

```http
Authorization: Bearer <your_token>
```

