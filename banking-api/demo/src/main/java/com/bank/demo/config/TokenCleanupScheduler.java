package com.bank.demo.config;
import java.time.Instant;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.bank.demo.repository.BlacklistedTokenRepository;

@Component
public class TokenCleanupScheduler {

    private final BlacklistedTokenRepository blacklistedTokenRepository;

    public TokenCleanupScheduler(BlacklistedTokenRepository repo) {
        this.blacklistedTokenRepository = repo;
    }

    // Runs once every hour
    @Scheduled(fixedRate = 3600000)
    public void cleanExpiredTokens() {
        blacklistedTokenRepository.deleteByExpiryBefore(Instant.now());
        System.out.println("🧹 Expired tokens cleaned up");
    }
}