package com.bank.demo.model;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.UUID;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import com.bank.demo.model.enums.TransactionStatus;
import com.bank.demo.model.enums.TransactionType;

import jakarta.persistence.Column;
import jakarta.persistence.Entity ;
import jakarta.persistence.EnumType ;
import jakarta.persistence.Enumerated ;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "transactions")
@Getter @Setter
@IdClass(TransactionId.class)
public class Transaction {

    @Id
    @GeneratedValue(generator = "uuid2")
    @Column(name = "transaction_id", columnDefinition = "uuid")
    private UUID transactionId;

    @Id
    @Column(name = "created_at")
    private OffsetDateTime createdAt = OffsetDateTime.now();

    @ManyToOne
    @JoinColumn(name = "from_account_id")
    private Account fromAccount;

    @ManyToOne
    @JoinColumn(name = "to_account_id")
    private Account toAccount;

    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_type", nullable = false)
    private TransactionType transactionType;

    private BigDecimal amount;

    private String currency = "CAD";

    private String description;

    @Column(name = "reference_number")
    private String referenceNumber;

    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_status")
    private TransactionStatus transactionStatus = TransactionStatus.PENDING;

    @Column(name = "processed_at")
    private OffsetDateTime processedAt;

    @Column(name = "scheduled_at")
    private OffsetDateTime scheduledAt;

    @Column(name = "fee_amount")
    private BigDecimal feeAmount = BigDecimal.ZERO;

    @Column(name = "exchange_rate")
    private BigDecimal exchangeRate = BigDecimal.ONE;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "merchant_info")
    private Map<String, Object> merchantInfo;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "location_info")
    private Map<String, Object> locationInfo;

    @Column(name = "updated_at")
    private OffsetDateTime updatedAt = OffsetDateTime.now();
}
