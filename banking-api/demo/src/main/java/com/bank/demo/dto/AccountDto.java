package com.bank.demo.dto;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

import com.bank.demo.model.enums.AccountStatus;
import com.bank.demo.model.enums.AccountType;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AccountDto {
    private UUID id;
    private String accountNumber;
    private UUID userId;
    private String userFirstName;
    private String userLastName;
    // Bank fields removed - were unused
    private AccountType accountType;
    private AccountStatus accountStatus;
    private BigDecimal balance;
    private BigDecimal availableBalance;
    private BigDecimal creditLimit;
    private BigDecimal interestRate;
    private BigDecimal overdraftLimit;
    private BigDecimal minimumBalance;
    private OffsetDateTime openedAt;
    private OffsetDateTime closedAt;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}