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
import com.bank.demo.repository.Userepository;

@Service
public class TransactionService {

    @Autowired
    private transactionRepository transactionRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private Userepository userRepository;

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

    @Transactional
    public Transaction transferByEmail(String senderEmail, String recipientEmail, BigDecimal amount,
            String description) {
        // Find sender's primary account by email
        Account fromAccount = accountRepository.findPrimaryAccountByUserEmail(senderEmail)
                .orElseThrow(() -> new RuntimeException("Sender account not found for email: " + senderEmail));

        // Find recipient's primary account by email
        Account toAccount = accountRepository.findPrimaryAccountByUserEmail(recipientEmail)
                .orElseThrow(() -> new RuntimeException("Recipient account not found for email: " + recipientEmail));

        // Prevent self-transfer
        if (senderEmail.equalsIgnoreCase(recipientEmail)) {
            throw new RuntimeException("Cannot transfer to yourself");
        }

        // Validate sufficient balance
        if (fromAccount.getAvailableBalance().compareTo(amount) < 0) {
            throw new RuntimeException("Insufficient balance. Available: " + fromAccount.getAvailableBalance());
        }

        // Create transaction and set it to PENDING
        Transaction transaction = new Transaction();
        transaction.setFromAccount(fromAccount);
        transaction.setToAccount(toAccount);
        transaction.setTransactionType(TransactionType.TRANSFER);
        transaction.setAmount(amount);
        transaction.setDescription(description != null ? description : "Email transfer to " + recipientEmail);
        transaction.setReferenceNumber(generateReferenceNumber());
        transaction.setTransactionStatus(TransactionStatus.PENDING); // Transaction requires recipient's approval
        transaction.setCreatedAt(OffsetDateTime.now());
        // ProcessedAt should be null until it's completed or cancelled
        transaction.setProcessedAt(null); 

        Transaction savedTransaction = transactionRepository.save(transaction);

        // Debit the sender's account immediately
        fromAccount.setBalance(fromAccount.getBalance().subtract(amount));
        fromAccount.setAvailableBalance(fromAccount.getAvailableBalance().subtract(amount));
        accountRepository.save(fromAccount);
        
        // The recipient's account is NOT credited until they accept the transaction.

        System.out.println("DEBUG: Email transfer initiated (PENDING) - ID: " + savedTransaction.getTransactionId() +
                ", Amount: " + amount + ", From: " + senderEmail + ", To: " + recipientEmail);

        return savedTransaction;
    }

    private String generateReferenceNumber() {
        return "TXN" + System.currentTimeMillis();
    }

    @Transactional
    public Transaction updateTransactionStatus(UUID transactionId, TransactionStatus status, String userEmail) {
        List<Transaction> transactions = transactionRepository.findByTransactionId(transactionId);
        if (transactions.isEmpty()) {
            throw new RuntimeException("Transaction not found for ID: " + transactionId);
        }
        // Assuming the most recent transaction is the one to update if multiple exist
        Transaction transaction = transactions.stream()
                .sorted((t1, t2) -> t2.getCreatedAt().compareTo(t1.getCreatedAt()))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("Transaction not found for ID: " + transactionId));

        Account toAccount = transaction.getToAccount();
        if (toAccount == null) {
            throw new RuntimeException("Invalid transaction: No target account specified.");
        }

        // Only the recipient can accept or refuse a PENDING transfer.
        if (!toAccount.getUser().getEmail().equalsIgnoreCase(userEmail)) {
            throw new RuntimeException("Unauthorized: You are not the recipient of this transaction.");
        }

        if (transaction.getTransactionStatus() != TransactionStatus.PENDING) {
            throw new RuntimeException("Transaction is not in a PENDING state and cannot be updated.");
        }

        if (status == TransactionStatus.COMPLETED) {
            // The recipient accepts the transaction.
            // The amount was already debited from the sender, now we credit the recipient.
            transaction.setTransactionStatus(TransactionStatus.COMPLETED);
            transaction.setProcessedAt(OffsetDateTime.now());

            BigDecimal amount = transaction.getAmount();
            toAccount.setBalance(toAccount.getBalance().add(amount));
            toAccount.setAvailableBalance(toAccount.getAvailableBalance().add(amount));
            accountRepository.save(toAccount);

        } else if (status == TransactionStatus.CANCELLED || status == TransactionStatus.FAILED) {
            // The recipient refuses the transaction, or it failed.
            // The amount is refunded to the sender.
            transaction.setTransactionStatus(status);
            transaction.setProcessedAt(OffsetDateTime.now());

            Account fromAccount = transaction.getFromAccount();
            if (fromAccount != null) {
                BigDecimal amount = transaction.getAmount();
                fromAccount.setBalance(fromAccount.getBalance().add(amount));
                fromAccount.setAvailableBalance(fromAccount.getAvailableBalance().add(amount));
                accountRepository.save(fromAccount);
            }
        } else {
            throw new RuntimeException("Invalid status update. Only COMPLETED, CANCELLED, or FAILED are permitted.");
        }

        return transactionRepository.save(transaction);
    }
}