// Banking Application Java Models
// Using JPA/Hibernate annotations for ORM mapping

import javax.persistence.*;
import javax.validation.constraints.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonIgnore;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

// ============= ENUMS =============

public enum AccountType {
    CHECKING, SAVINGS, CREDIT, LOAN
}

public enum AccountStatus {
    ACTIVE, INACTIVE, SUSPENDED, CLOSED
}

public enum TransactionType {
    DEPOSIT, WITHDRAWAL, TRANSFER, PAYMENT, FEE
}

public enum TransactionStatus {
    PENDING, COMPLETED, FAILED, CANCELLED
}

public enum UserRole {
    CUSTOMER, EMPLOYEE, MANAGER, ADMIN
}

// ============= ENTITIES =============

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "user_id")
    private UUID userId;
    
    @Column(unique = true, nullable = false, length = 50)
    private String username;
    
    @Email
    @Column(unique = true, nullable = false, length = 100)
    private String email;
    
    @JsonIgnore
    @Column(name = "password_hash", nullable = false)
    private String passwordHash;
    
    @NotBlank
    @Column(name = "first_name", nullable = false, length = 100)
    private String firstName;
    
    @NotBlank
    @Column(name = "last_name", nullable = false, length = 100)
    private String lastName;
    
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$")
    private String phone;
    
    @Column(name = "date_of_birth")
    private LocalDate dateOfBirth;
    
    @JsonIgnore
    @Column(name = "ssn_hash")
    private String ssnHash;
    
    @Column(columnDefinition = "jsonb")
    private String address; // JSON string for flexible address structure
    
    @Enumerated(EnumType.STRING)
    private UserRole role = UserRole.CUSTOMER;
    
    @Column(name = "is_active")
    private Boolean isActive = true;
    
    @Column(name = "email_verified")
    private Boolean emailVerified = false;
    
    @Column(name = "failed_login_attempts")
    private Integer failedLoginAttempts = 0;
    
    @Column(name = "last_login_at")
    private LocalDateTime lastLoginAt;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();
    
    // Relationships
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Account> accounts;
    
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<Beneficiary> beneficiaries;
}

@Entity
@Table(name = "banks")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Bank {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "bank_id")
    private UUID bankId;
    
    @NotBlank
    @Column(name = "bank_name", nullable = false, length = 200)
    private String bankName;
    
    @Pattern(regexp = "^\\d{9}$")
    @Column(name = "routing_number", unique = true, nullable = false, length = 9)
    private String routingNumber;
    
    @Column(name = "swift_code", length = 11)
    private String swiftCode;
    
    @Column(columnDefinition = "jsonb")
    private String address;
    
    @Column(name = "contact_info", columnDefinition = "jsonb")
    private String contactInfo;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
    
    // Relationships
    @OneToMany(mappedBy = "bank", cascade = CascadeType.ALL)
    private List<Account> accounts;
}

@Entity
@Table(name = "accounts")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Account {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "account_id")
    private UUID accountId;
    
    @Column(name = "account_number", unique = true, nullable = false, length = 20)
    private String accountNumber;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "bank_id", nullable = false)
    private Bank bank;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "account_type", nullable = false)
    private AccountType accountType;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "account_status")
    private AccountStatus accountStatus = AccountStatus.ACTIVE;
    
    @DecimalMin(value = "0.0", inclusive = true)
    @Digits(integer = 13, fraction = 2)
    private BigDecimal balance = BigDecimal.ZERO;
    
    @Column(name = "available_balance")
    @Digits(integer = 13, fraction = 2)
    private BigDecimal availableBalance = BigDecimal.ZERO;
    
    @Column(name = "credit_limit")
    @Digits(integer = 13, fraction = 2)
    private BigDecimal creditLimit = BigDecimal.ZERO;
    
    @Column(name = "interest_rate")
    @Digits(integer = 1, fraction = 4)
    private BigDecimal interestRate = BigDecimal.ZERO;
    
    @Column(name = "overdraft_limit")
    @Digits(integer = 8, fraction = 2)
    private BigDecimal overdraftLimit = BigDecimal.ZERO;
    
    @Column(name = "minimum_balance")
    @Digits(integer = 8, fraction = 2)
    private BigDecimal minimumBalance = BigDecimal.ZERO;
    
    @Column(name = "account_metadata", columnDefinition = "jsonb")
    private String accountMetadata;
    
    @Column(name = "opened_at")
    private LocalDateTime openedAt = LocalDateTime.now();
    
    @Column(name = "closed_at")
    private LocalDateTime closedAt;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();
    
    // Relationships
    @OneToMany(mappedBy = "fromAccount", cascade = CascadeType.ALL)
    private List<Transaction> outgoingTransactions;
    
    @OneToMany(mappedBy = "toAccount", cascade = CascadeType.ALL)
    private List<Transaction> incomingTransactions;
    
    @OneToMany(mappedBy = "account", cascade = CascadeType.ALL)
    private List<Card> cards;
    
    @OneToMany(mappedBy = "account", cascade = CascadeType.ALL)
    private List<AccountHolder> accountHolders;
    
    // Helper methods
    public boolean isActive() {
        return AccountStatus.ACTIVE.equals(this.accountStatus);
    }
    
    public boolean hasSufficientBalance(BigDecimal amount) {
        return this.availableBalance.compareTo(amount) >= 0;
    }
}

@Entity
@Table(name = "transactions")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Transaction {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "transaction_id")
    private UUID transactionId;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "from_account_id")
    private Account fromAccount;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "to_account_id")
    private Account toAccount;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_type", nullable = false)
    private TransactionType transactionType;
    
    @DecimalMin(value = "0.01")
    @Digits(integer = 13, fraction = 2)
    @Column(nullable = false)
    private BigDecimal amount;
    
    @Column(length = 3)
    private String currency = "USD";
    
    private String description;
    
    @Column(name = "reference_number", unique = true, length = 50)
    private String referenceNumber;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_status")
    private TransactionStatus transactionStatus = TransactionStatus.PENDING;
    
    @Column(name = "processed_at")
    private LocalDateTime processedAt;
    
    @Column(name = "scheduled_at")
    private LocalDateTime scheduledAt;
    
    @Column(name = "fee_amount")
    @Digits(integer = 8, fraction = 2)
    private BigDecimal feeAmount = BigDecimal.ZERO;
    
    @Column(name = "exchange_rate")
    @Digits(integer = 4, fraction = 6)
    private BigDecimal exchangeRate = BigDecimal.ONE;
    
    @Column(name = "merchant_info", columnDefinition = "jsonb")
    private String merchantInfo;
    
    @Column(name = "location_info", columnDefinition = "jsonb")
    private String locationInfo;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();
    
    // Helper methods
    public boolean isCompleted() {
        return TransactionStatus.COMPLETED.equals(this.transactionStatus);
    }
    
    public boolean isPending() {
        return TransactionStatus.PENDING.equals(this.transactionStatus);
    }
    
    public BigDecimal getTotalAmount() {
        return this.amount.add(this.feeAmount);
    }
}

@Entity
@Table(name = "account_holders")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AccountHolder {
    
    @EmbeddedId
    private AccountHolderId id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @MapsId("accountId")
    @JoinColumn(name = "account_id")
    private Account account;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @MapsId("userId")
    @JoinColumn(name = "user_id")
    private User user;
    
    @Column(length = 50)
    private String relationship = "PRIMARY";
    
    @Column(columnDefinition = "jsonb")
    private String permissions;
    
    @Column(name = "added_at")
    private LocalDateTime addedAt = LocalDateTime.now();
}

@Embeddable
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AccountHolderId {
    @Column(name = "account_id")
    private UUID accountId;
    
    @Column(name = "user_id")
    private UUID userId;
}

@Entity
@Table(name = "cards")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Card {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "card_id")
    private UUID cardId;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "account_id", nullable = false)
    private Account account;
    
    @JsonIgnore
    @Column(name = "card_number_hash", nullable = false)
    private String cardNumberHash;
    
    @Column(name = "card_type", nullable = false, length = 20)
    private String cardType;
    
    @Future
    @Column(name = "expiry_date", nullable = false)
    private LocalDate expiryDate;
    
    @JsonIgnore
    @Column(name = "cvv_hash")
    private String cvvHash;
    
    @Column(name = "card_status", length = 20)
    private String cardStatus = "ACTIVE";
    
    @Column(name = "daily_limit")
    @Digits(integer = 8, fraction = 2)
    private BigDecimal dailyLimit = new BigDecimal("1000.00");
    
    @Column(name = "monthly_limit")
    @Digits(integer = 10, fraction = 2)
    private BigDecimal monthlyLimit = new BigDecimal("10000.00");
    
    @Column(name = "is_contactless")
    private Boolean isContactless = true;
    
    @Column(name = "issued_at")
    private LocalDateTime issuedAt = LocalDateTime.now();
    
    @Column(name = "blocked_at")
    private LocalDateTime blockedAt;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
    
    // Helper methods
    public boolean isActive() {
        return "ACTIVE".equals(this.cardStatus);
    }
    
    public boolean isExpired() {
        return this.expiryDate.isBefore(LocalDate.now());
    }
}

@Entity
@Table(name = "beneficiaries")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Beneficiary {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "beneficiary_id")
    private UUID beneficiaryId;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(length = 100)
    private String nickname;
    
    @NotBlank
    @Column(name = "account_number", nullable = false, length = 20)
    private String accountNumber;
    
    @Pattern(regexp = "^\\d{9}$")
    @Column(name = "routing_number", length = 9)
    private String routingNumber;
    
    @Column(name = "bank_name", length = 200)
    private String bankName;
    
    @NotBlank
    @Column(name = "beneficiary_name", nullable = false, length = 200)
    private String beneficiaryName;
    
    @Column(length = 100)
    private String relationship;
    
    @Column(name = "is_verified")
    private Boolean isVerified = false;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}

@Entity
@Table(name = "audit_logs")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AuditLog {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "audit_id")
    private UUID auditId;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;
    
    @Column(nullable = false, length = 100)
    private String action;
    
    @Column(name = "table_name", length = 50)
    private String tableName;
    
    @Column(name = "record_id")
    private UUID recordId;
    
    @Column(name = "old_values", columnDefinition = "jsonb")
    private String oldValues;
    
    @Column(name = "new_values", columnDefinition = "jsonb")
    private String newValues;
    
    @Column(name = "ip_address")
    private String ipAddress;
    
    @Column(name = "user_agent", columnDefinition = "text")
    private String userAgent;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}

// ============= DTOs =============

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AccountSummaryDTO {
    private UUID accountId;
    private String accountNumber;
    private AccountType accountType;
    private BigDecimal balance;
    private BigDecimal availableBalance;
    private String firstName;
    private String lastName;
    private String email;
    private String bankName;
    private AccountStatus status;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TransactionDTO {
    private UUID transactionId;
    private TransactionType transactionType;
    private BigDecimal amount;
    private String currency;
    private String description;
    private TransactionStatus status;
    private LocalDateTime createdAt;
    private String fromAccountNumber;
    private String toAccountNumber;
    private BigDecimal feeAmount;
    private String referenceNumber;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TransferRequestDTO {
    @NotNull
    private UUID fromAccountId;
    
    @NotNull
    private UUID toAccountId;
    
    @NotNull
    @DecimalMin(value = "0.01")
    private BigDecimal amount;
    
    @Size(max = 255)
    private String description;
    
    private LocalDateTime scheduledAt;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserRegistrationDTO {
    @NotBlank
    @Size(min = 3, max = 50)
    private String username;
    
    @Email
    @NotBlank
    private String email;
    
    @NotBlank
    @Size(min = 8)
    private String password;
    
    @NotBlank
    private String firstName;
    
    @NotBlank
    private String lastName;
    
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$")
    private String phone;
    
    @Past
    private LocalDate dateOfBirth;
    
    private String address;
}
