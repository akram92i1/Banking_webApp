package com.bank.demo.repository;

import java.time.OffsetDateTime;
import java.time.LocalDateTime;
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
    
    // AI Agent specific queries for threat detection and analysis
    @Query("SELECT t FROM Transaction t WHERE " +
           "(t.amount > 10000 OR t.amount < -10000 OR " +
           "t.createdAt > :recentTime) " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findSuspiciousTransactionsSince(@Param("recentTime") OffsetDateTime recentTime);
    
    // Default method for suspicious transactions (last 24 hours with large amounts)
    @Query("SELECT t FROM Transaction t WHERE " +
           "(t.amount > 5000 OR t.amount < -5000) OR " +
           "t.createdAt > :oneDayAgo " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findSuspiciousTransactions(@Param("oneDayAgo") OffsetDateTime oneDayAgo);
    
    @Query("SELECT t FROM Transaction t WHERE " +
           "(t.fromAccount.user.id = :userId OR t.toAccount.user.id = :userId) " +
           "AND t.createdAt > :startDate " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findByUserIdAndDateRange(@Param("userId") UUID userId, @Param("startDate") OffsetDateTime startDate);
    
    @Query("SELECT t FROM Transaction t WHERE " +
           "t.amount < 0 AND t.fromAccount.user.id = :userId " +
           "AND t.createdAt > :startDate " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findSpendingTransactionsByUserId(@Param("userId") UUID userId, @Param("startDate") OffsetDateTime startDate);
    
    @Query("SELECT COUNT(t) FROM Transaction t WHERE t.createdAt > :startDate")
    Long countTransactionsSince(@Param("startDate") OffsetDateTime startDate);
    
    @Query("SELECT t FROM Transaction t WHERE " +
           "t.createdAt BETWEEN :startDate AND :endDate " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findTransactionsBetweenDates(@Param("startDate") OffsetDateTime startDate, @Param("endDate") OffsetDateTime endDate);
    
    // Simple version for AI integration without pagination
    @Query("SELECT t FROM Transaction t " +
           "WHERE t.fromAccount.user.id = :userId " +
           "OR t.toAccount.user.id = :userId " +
           "ORDER BY t.createdAt DESC")
    List<Transaction> findByUserIdOrderByCreatedAtDesc(@Param("userId") UUID userId);
}
