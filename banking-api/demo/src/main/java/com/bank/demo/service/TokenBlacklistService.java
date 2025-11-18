package com.bank.demo.service;

import java.time.Instant;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.model.BlacklistedToken;
import com.bank.demo.repository.BlacklistedTokenRepository;

@Service
public class TokenBlacklistService {

    @Autowired
    private BlacklistedTokenRepository blacklistedTokenRepository;

    public void blacklistToken(String token, Instant expiry) {
        System.out.println(">>> Blacklisting token: " + token.substring(0, 20) + "...");
        if (!blacklistedTokenRepository.existsByToken(token)) {
            blacklistedTokenRepository.save(new BlacklistedToken(token, expiry));
            System.out.println(">>> Token blacklisted successfully: " + token.substring(0, 20) + "...");
        }
    }

    public boolean isTokenBlacklisted(String token) {
        return blacklistedTokenRepository.existsByToken(token);
    }

    // Optional cleanup for expired tokens
    public void cleanupExpiredTokens() {
        blacklistedTokenRepository.findAll().stream()
            .filter(t -> t.getExpiry().isBefore(Instant.now()))
            .forEach(t -> blacklistedTokenRepository.delete(t));
    }
}
