package com.bank.demo.service;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bank.demo.model.Account;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.enums.TransactionStatus;
import com.bank.demo.model.enums.TransactionType;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.transactionRepository;

@Service
public class TransactionService {

    @Autowired
    private transactionRepository transactionRepository;
    
    @Autowired
    private AccountRepository accountRepository;

    public List<Transaction> getTransactionsByUserId(UUID userId, int limit) {
        PageRequest pageRequest = PageRequest.of(0, limit, Sort.by(Sort.Direction.DESC, "createdAt"));
        return transactionRepository.findByUserIdOrderByCreatedAtDesc(userId, pageRequest);
    }

    public List<Transaction> getTransactionsByAccountId(UUID accountId, int limit) {
        PageRequest pageRequest = PageRequest.of(0, limit, Sort.by(Sort.Direction.DESC, "createdAt"));
        return transactionRepository.findByAccountIdOrderByCreatedAtDesc(accountId, pageRequest);
    }

    @Transactional
    public Transaction transfer(UUID fromAccountId, UUID toAccountId, BigDecimal amount, String description) {
        Account fromAccount = accountRepository.findById(fromAccountId)
            .orElseThrow(() -> new RuntimeException("From account not found"));
        Account toAccount = accountRepository.findById(toAccountId)
            .orElseThrow(() -> new RuntimeException("To account not found"));
        
        // Validate sufficient balance
        if (fromAccount.getAvailableBalance().compareTo(amount) < 0) {
            throw new RuntimeException("Insufficient balance");
        }
        
        // Create transaction
        Transaction transaction = new Transaction();
        transaction.setFromAccount(fromAccount);
        transaction.setToAccount(toAccount);
        transaction.setTransactionType(TransactionType.TRANSFER);
        transaction.setAmount(amount);
        transaction.setDescription(description);
        transaction.setReferenceNumber(generateReferenceNumber());
        transaction.setTransactionStatus(TransactionStatus.COMPLETED); // Assuming instant transfer for demo
        transaction.setCreatedAt(OffsetDateTime.now());
        transaction.setProcessedAt(OffsetDateTime.now());
        
        Transaction savedTransaction = transactionRepository.save(transaction);
        
        // Update balances
        fromAccount.setBalance(fromAccount.getBalance().subtract(amount));
        fromAccount.setAvailableBalance(fromAccount.getAvailableBalance().subtract(amount));
        toAccount.setBalance(toAccount.getBalance().add(amount));
        toAccount.setAvailableBalance(toAccount.getAvailableBalance().add(amount));
        
        accountRepository.save(fromAccount);
        accountRepository.save(toAccount);
        
        return savedTransaction;
    }
    
    @Transactional
    public Transaction deposit(UUID accountId, BigDecimal amount, String description) {
        Account account = accountRepository.findById(accountId)
            .orElseThrow(() -> new RuntimeException("Account not found"));
        
        Transaction transaction = new Transaction();
        transaction.setToAccount(account);
        transaction.setTransactionType(TransactionType.DEPOSIT);
        transaction.setAmount(amount);
        transaction.setDescription(description);
        transaction.setReferenceNumber(generateReferenceNumber());
        transaction.setTransactionStatus(TransactionStatus.COMPLETED);
        transaction.setCreatedAt(OffsetDateTime.now());
        transaction.setProcessedAt(OffsetDateTime.now());
        
        Transaction savedTransaction = transactionRepository.save(transaction);
        
        // Update balance
        account.setBalance(account.getBalance().add(amount));
        account.setAvailableBalance(account.getAvailableBalance().add(amount));
        accountRepository.save(account);
        
        return savedTransaction;
    }
    
    private String generateReferenceNumber() {
        return "TXN" + System.currentTimeMillis();
    }
}