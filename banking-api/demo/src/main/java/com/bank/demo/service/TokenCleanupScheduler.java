package com.bank.demo.service;

import java.time.Instant;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bank.demo.repository.BlacklistedTokenRepository;

@Service
public class TokenCleanupScheduler {

    private static final Logger logger = LoggerFactory.getLogger(TokenCleanupScheduler.class);

    @Autowired
    private BlacklistedTokenRepository blacklistedTokenRepository;

    /**
     * Scheduled task to clean up expired blacklisted tokens
     * Runs every hour at minute 0
     */
    @Scheduled(cron = "0 0 * * * ?")
    @Transactional
    public void cleanupExpiredTokens() {
        try {
            logger.info("🧹 Starting cleanup of expired blacklisted tokens...");
            
            Instant now = Instant.now();
            long countBefore = blacklistedTokenRepository.count();
            
            // Delete expired tokens
            blacklistedTokenRepository.deleteByExpiryBefore(now);
            
            long countAfter = blacklistedTokenRepository.count();
            long deletedCount = countBefore - countAfter;
            
            if (deletedCount > 0) {
                logger.info("✅ Cleaned up {} expired blacklisted tokens. Remaining tokens: {}", 
                           deletedCount, countAfter);
            } else {
                logger.debug("🔍 No expired tokens found to clean up. Total tokens: {}", countAfter);
            }
            
        } catch (Exception e) {
            logger.error("❌ Error during token cleanup: {}", e.getMessage(), e);
        }
    }

    /**
     * Manual cleanup method (can be called programmatically if needed)
     * @return number of tokens deleted
     */
    @Transactional
    public long manualCleanup() {
        try {
            logger.info("🧹 Manual cleanup of expired blacklisted tokens requested...");
            
            Instant now = Instant.now();
            long countBefore = blacklistedTokenRepository.count();
            
            blacklistedTokenRepository.deleteByExpiryBefore(now);
            
            long countAfter = blacklistedTokenRepository.count();
            long deletedCount = countBefore - countAfter;
            
            logger.info("✅ Manual cleanup completed. Deleted {} tokens. Remaining: {}", 
                       deletedCount, countAfter);
            
            return deletedCount;
            
        } catch (Exception e) {
            logger.error("❌ Error during manual token cleanup: {}", e.getMessage(), e);
            throw e;
        }
    }

    /**
     * Get current blacklisted token statistics
     * @return array with [total tokens, expired tokens]
     */
    public long[] getTokenStatistics() {
        try {
            long totalTokens = blacklistedTokenRepository.count();
            
            // Count expired tokens (tokens with expiry before now)
            Instant now = Instant.now();
            long expiredTokens = blacklistedTokenRepository.findAll().stream()
                .mapToLong(token -> token.getExpiry().isBefore(now) ? 1 : 0)
                .sum();
            
            return new long[]{totalTokens, expiredTokens};
            
        } catch (Exception e) {
            logger.error("❌ Error getting token statistics: {}", e.getMessage());
            return new long[]{0, 0};
        }
    }
}