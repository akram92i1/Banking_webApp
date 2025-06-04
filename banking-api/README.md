# ⚙️ Banking API

This service provides the core business logic and RESTful endpoints for managing accounts, transactions, and banking operations in the Banking Platform.

## Features

- Account creation and management
- Transaction processing (deposit, withdrawal, transfer, payment)
- Beneficiary management
- Audit logging
- Role-based access control

## Tech Stack

- Java 17+
- Spring Boot
- Spring Data JPA (Hibernate)
- PostgreSQL
- Lombok

## Project Structure

```
banking-api/
│
├── controller/      # REST controllers for API endpoints
├── service/         # Business logic and service classes
├── repository/      # Spring Data JPA repositories
├── model/           # Entity classes and enums
│   └── enums/       # Enum types (UserRole, AccountType, etc.)
├── dto/             # Data Transfer Objects
├── config/          # Configuration classes
├── exception/       # Custom exception classes
├── BankingApiApplication.java  # Main Spring Boot application
└── README.md        # Project documentation
```

## Getting Started

1. **Install dependencies and build:**
   ```
   ./mvnw clean install
   ```
2. **Set environment variables or configure `application.properties` for your database.**
3. **Run the application:**
   ```
   ./mvnw spring-boot:run
   ```

## Environment Variables

- `SPRING_DATASOURCE_URL` – JDBC URL for PostgreSQL
- `SPRING_DATASOURCE_USERNAME` – Database username
- `SPRING_DATASOURCE_PASSWORD` – Database password

## API Endpoints

- `POST /accounts` – Create a new account
- `GET /accounts/{id}` – Get account details
- `POST /transactions` – Create a transaction
- `GET /transactions/{id}` – Get transaction details
- ...and more

## License

MIT