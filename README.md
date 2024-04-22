## XB-DB: The Ultimate Spectroscopic Database for X-ray Binaries



### Deployment Instructions

The application is orchestrated using Docker Compose, which manages two main services: `web` for the web application and `db` for the database backend.

To deploy the application, follow these steps:

1. **Build Docker containers:** This command builds the Docker containers defined in the `docker-compose.prod.yml` file. It sets up the environment for running the application.

    ```bash
    docker-compose -f docker-compose.prod.yml up --build -d
    ```

2. **Apply database migrations:** After the containers are up and running, apply any pending database migrations using the following command. This ensures that the database schema is up-to-date with the latest changes.

    ```bash
    docker-compose exec web python manage.py migrate
    ```

3. **Collect static files:** Static files such as CSS, JavaScript, and images need to be collected from your Django app and served in production. Use the following command to collect these files.

    ```bash
    docker-compose exec web python manage.py collectstatic --noinput
    ```

4. **Create a superuser (optional):** If you require administrative access to the Django admin interface, create a superuser account using this command. It allows you to manage the application's data and settings.

    ```bash
    docker-compose exec web python manage.py createsuperuser 
    ```



Once deployed, the application will be accessible at  `http://localhost:8000`
