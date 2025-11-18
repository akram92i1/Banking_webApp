package com.bank.demo.model;

import java.time.Instant;
import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "blacklisted_tokens")
public class BlacklistedToken {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(nullable = false, unique = true, columnDefinition = "TEXT")
    private String token;

    @Column(nullable = false)
    private Instant expiry;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    public BlacklistedToken(String token , Instant expiry) {
        this.token = token;
        this.expiry = expiry;
    }

    public String getToken() {
        return token;
    }

    public Instant getExpiry() {
        return expiry;
    }
    
}
