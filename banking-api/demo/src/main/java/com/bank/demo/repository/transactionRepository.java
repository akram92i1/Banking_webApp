package com.bank.demo.repository;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.bank.demo.model.Transaction;
import com.bank.demo.model.TransactionId;
@Repository
public interface  transactionRepository extends JpaRepository  <Transaction,TransactionId>{
    // Custom query methods can be defined here if needed
        // Find by just the transaction UUID (ignoring the createdAt part of composite key)
    List<Transaction> findByTransactionId(UUID transactionId);

    // Find by the complete composite key
    Optional<Transaction> findByTransactionIdAndCreatedAt(UUID transactionId, OffsetDateTime createdAt);
    
}
