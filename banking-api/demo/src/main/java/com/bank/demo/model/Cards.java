package com.bank.demo.model;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "cards")
@Getter @Setter
public class Cards {
    @Id
    @GeneratedValue(generator = "uuid2")
    @Column(name = "card_id", columnDefinition = "uuid2")
    private UUID id;

    @ManyToOne(fetch = jakarta.persistence.FetchType.LAZY)
    @JoinColumn(name = "account_id", nullable = false)
    @JsonIgnore // Prevent full Account object from being serialized
    private Account account;

    @JsonProperty("accountId")
    public UUID getAccountId() {
        return account != null ? account.getId() : null;
    }


    @Column(name="card_number_hash" , nullable = false )
    private String cardNumberHash;
    
    @Column(name="card_type", nullable = false)
    private String cardType;
    
    @Column(name="expiry_date", nullable = false)
    private OffsetDateTime expiryDate;

    @Column(name="cvv_hash", nullable = false)
    private String cvvHash;

    @Column(name = "card_status")
    private String cardStatus;

    @Column(name = "daily_limit")
    private BigDecimal dailyLimit;

    @Column(name = "monthly_limit")
    private BigDecimal monthlyLimit;

    @Column(name = "is_contactless")
    private Boolean isContactless;

    @Column(name = "issued_at")
    private OffsetDateTime issuedAt;

    @Column(name = "blocked_at")
    private OffsetDateTime blockedAt;

    @Column(name = "created_at")
    private OffsetDateTime createdAt;

}
