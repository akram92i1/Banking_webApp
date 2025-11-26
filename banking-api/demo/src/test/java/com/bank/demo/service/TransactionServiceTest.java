package com.bank.demo.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.Optional;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.bank.demo.model.Account;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.enums.TransactionStatus;
import com.bank.demo.model.enums.TransactionType;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.transactionRepository;

@ExtendWith(MockitoExtension.class)
public class TransactionServiceTest {

    @Mock
    private transactionRepository transactionRepository;

    @Mock
    private AccountRepository accountRepository;

    @InjectMocks
    private TransactionService transactionService;

    @Test
    void deposit_ShouldIncreaseBalanceAndSaveTransaction() {
        // Arrange
        UUID accountId = UUID.randomUUID();
        BigDecimal initialBalance = new BigDecimal("100.00");
        BigDecimal depositAmount = new BigDecimal("50.00");
        
        Account account = new Account();
        account.setId(accountId);
        account.setBalance(initialBalance);
        account.setAvailableBalance(initialBalance);

        when(accountRepository.findById(accountId)).thenReturn(Optional.of(account));
        when(transactionRepository.save(any(Transaction.class))).thenAnswer(invocation -> invocation.getArgument(0));

        // Act
        Transaction result = transactionService.deposit(accountId, depositAmount, "Test Deposit");

        // Assert
        assertNotNull(result);
        assertEquals(TransactionType.DEPOSIT, result.getTransactionType());
        assertEquals(depositAmount, result.getAmount());
        assertEquals(TransactionStatus.COMPLETED, result.getTransactionStatus());
        
        assertEquals(new BigDecimal("150.00"), account.getBalance());
        assertEquals(new BigDecimal("150.00"), account.getAvailableBalance());
        
        verify(accountRepository).save(account);
        verify(transactionRepository).save(any(Transaction.class));
    }

    @Test
    void transfer_ShouldTransferMoneyBetweenAccounts() {
        // Arrange
        UUID fromAccountId = UUID.randomUUID();
        UUID toAccountId = UUID.randomUUID();
        BigDecimal transferAmount = new BigDecimal("50.00");
        
        Account fromAccount = new Account();
        fromAccount.setId(fromAccountId);
        fromAccount.setBalance(new BigDecimal("100.00"));
        fromAccount.setAvailableBalance(new BigDecimal("100.00"));
        
        Account toAccount = new Account();
        toAccount.setId(toAccountId);
        toAccount.setBalance(new BigDecimal("50.00"));
        toAccount.setAvailableBalance(new BigDecimal("50.00"));

        when(accountRepository.findById(fromAccountId)).thenReturn(Optional.of(fromAccount));
        when(accountRepository.findById(toAccountId)).thenReturn(Optional.of(toAccount));
        when(transactionRepository.save(any(Transaction.class))).thenAnswer(invocation -> invocation.getArgument(0));

        // Act
        Transaction result = transactionService.transfer(fromAccountId, toAccountId, transferAmount, "Test Transfer");

        // Assert
        assertNotNull(result);
        assertEquals(TransactionType.TRANSFER, result.getTransactionType());
        assertEquals(transferAmount, result.getAmount());
        assertEquals(TransactionStatus.COMPLETED, result.getTransactionStatus());
        
        assertEquals(new BigDecimal("50.00"), fromAccount.getBalance());
        assertEquals(new BigDecimal("100.00"), toAccount.getBalance());
        
        verify(accountRepository).save(fromAccount);
        verify(accountRepository).save(toAccount);
        verify(transactionRepository).save(any(Transaction.class));
    }

    @Test
    void transfer_ShouldThrowException_WhenInsufficientBalance() {
        // Arrange
        UUID fromAccountId = UUID.randomUUID();
        UUID toAccountId = UUID.randomUUID();
        BigDecimal transferAmount = new BigDecimal("150.00");
        
        Account fromAccount = new Account();
        fromAccount.setId(fromAccountId);
        fromAccount.setBalance(new BigDecimal("100.00"));
        fromAccount.setAvailableBalance(new BigDecimal("100.00"));
        
        Account toAccount = new Account();
        toAccount.setId(toAccountId);

        when(accountRepository.findById(fromAccountId)).thenReturn(Optional.of(fromAccount));
        when(accountRepository.findById(toAccountId)).thenReturn(Optional.of(toAccount));

        // Act & Assert
        assertThrows(RuntimeException.class, () -> {
            transactionService.transfer(fromAccountId, toAccountId, transferAmount, "Test Transfer");
        });
    }
}
