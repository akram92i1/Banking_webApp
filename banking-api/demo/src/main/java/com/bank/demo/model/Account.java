package com.bank.demo.model;


import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.UUID;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import com.bank.demo.model.enums.AccountStatus;
import com.bank.demo.model.enums.AccountType;
import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;


@Entity
@Table(name = "accounts" , schema = "public")
@Getter @Setter
public class Account {

    @Id
    @GeneratedValue(generator = "uuid2")
    @Column(name = "account_id", columnDefinition = "uuid")
    private UUID id;

    @Column(name = "account_number", unique = true, nullable = false)
    private String accountNumber;

    @ManyToOne(fetch = jakarta.persistence.FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = jakarta.persistence.FetchType.LAZY)
    @JoinColumn(name = "bank_id", nullable = false)
    private Bank bank;

    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Enumerated(EnumType.STRING)
    @Column(name = "account_type", nullable = false)
    private AccountType accountType;

    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Enumerated(EnumType.STRING)
    @Column(name = "account_status")
    private AccountStatus accountStatus = AccountStatus.ACTIVE;

    private BigDecimal balance = BigDecimal.ZERO;
    @Column(name = "available_balance")
    private BigDecimal availableBalance = BigDecimal.ZERO;

    @Column(name = "credit_limit")
    private BigDecimal creditLimit = BigDecimal.ZERO;

    @Column(name = "interest_rate")
    private BigDecimal interestRate = BigDecimal.ZERO;

    @Column(name = "overdraft_limit")
    private BigDecimal overdraftLimit = BigDecimal.ZERO;

    @Column(name = "minimum_balance")
    private BigDecimal minimumBalance = BigDecimal.ZERO;

    @JsonIgnore
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "account_metadata")
    private Map<String, Object> accountMetadata;

    @Column(name = "opened_at")
    private OffsetDateTime openedAt = OffsetDateTime.now();

    @Column(name = "closed_at")
    private OffsetDateTime closedAt;

    @Column(name = "created_at")
    private OffsetDateTime createdAt = OffsetDateTime.now();

    @Column(name = "updated_at")
    private OffsetDateTime updatedAt = OffsetDateTime.now();
}
