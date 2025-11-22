package com.bank.demo.repository;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.bank.demo.model.Transaction;
import com.bank.demo.model.TransactionId;
import com.bank.demo.model.enums.TransactionStatus;
@Repository
public interface  transactionRepository extends JpaRepository  <Transaction,TransactionId>{
    // Custom query methods can be defined here if needed
        // Find by just the transaction UUID (ignoring the createdAt part of composite key)
    List<Transaction> findByTransactionId(UUID transactionId);

    // Find by the complete composite key
    Optional<Transaction> findByTransactionIdAndCreatedAt(UUID transactionId, OffsetDateTime createdAt);

    // Custom query with JPQL
    @Query("SELECT t FROM Transaction t " +
           "WHERE t.toAccount.id = :recipientAccountId " +
           "AND t.transactionStatus = :status " +
           "ORDER BY t.createdAt DESC")
    public List <Transaction> findPendingTransactionsByRecipient(@Param("recipientAccountId") UUID recipientAccountId , @Param("status") TransactionStatus status );

    // Find transactions by user ID (from either sender or recipient accounts)
    @Query("SELECT t FROM Transaction t " +
           "WHERE t.fromAccount.user.id = :userId " +
           "OR t.toAccount.user.id = :userId " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findByUserIdOrderByCreatedAtDesc(@Param("userId") UUID userId, Pageable pageable);

    // Find transactions by account ID (from either sender or recipient)
    @Query("SELECT t FROM Transaction t " +
           "WHERE t.fromAccount.id = :accountId " +
           "OR t.toAccount.id = :accountId " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findByAccountIdOrderByCreatedAtDesc(@Param("accountId") UUID accountId, Pageable pageable);
}
