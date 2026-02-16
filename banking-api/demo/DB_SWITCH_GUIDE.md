# Switching to Docker PostgreSQL

## Option 1: Update Application Configuration (Recommended)
You can configure your application to point specifically to the Docker container, even if the Host Postgres is running.

1.  **Find Docker Port Mapping**:
    Run `sudo docker ps` to see which port the container is mapped to.
    - If it's `0.0.0.0:5432->5432/tcp`, it conflicts with the Host Postgres on port 5432.
    - If it's mapped to a different port (e.g., `5433`), change `spring.datasource.url` in `application.properties` to use that port.

2.  **Stop Host Postgres (If Ports Conflict)**:
    If both are trying to use port 5432, you must stop one. To stop the Host Postgres:
    ```bash
    sudo systemctl stop postgresql
    sudo systemctl disable postgresql
    ```
    Then restart your Docker container to ensure it binds to port 5432:
    ```bash
    sudo docker restart elegant_tu
    ```

## Option 2: Verify Connection
After switching, the application will attempt to connect to the Docker container.
- **Note**: The Docker database might not have the same data as your Host DB. You might need to re-run migration scripts or seed data if the `users` table is empty or missing.
