package com.bank.demo.model;

import java.io.Serializable;
import java.time.OffsetDateTime;
import java.util.Objects;
import java.util.UUID;

public class TransactionId implements Serializable {

    private UUID transactionId;
    private OffsetDateTime createdAt;

    // Default constructor (required by JPA)
    public TransactionId() {}

    public TransactionId(UUID transactionId, OffsetDateTime createdAt) {
        this.transactionId = transactionId;
        this.createdAt = createdAt;
    }

    // Getters and Setters
    public UUID getTransactionId() {
        return transactionId;
    }

    public void setTransactionId(UUID transactionId) {
        this.transactionId = transactionId;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(OffsetDateTime createdAt) {
        this.createdAt = createdAt;
    }

    // Required for composite keys
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof TransactionId)) return false;
        TransactionId that = (TransactionId) o;
        return Objects.equals(transactionId, that.transactionId) &&
               Objects.equals(createdAt, that.createdAt);
    }

    @Override
    public int hashCode() {
        return Objects.hash(transactionId, createdAt);
    }
}
