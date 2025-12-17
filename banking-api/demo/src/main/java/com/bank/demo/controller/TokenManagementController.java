package com.bank.demo.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.service.TokenCleanupScheduler;

@RestController
@RequestMapping("/api/admin/tokens")
public class TokenManagementController {

    @Autowired
    private TokenCleanupScheduler tokenCleanupScheduler;

    /**
     * Get current blacklisted token statistics
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getTokenStatistics() {
        try {
            long[] stats = tokenCleanupScheduler.getTokenStatistics();
            
            Map<String, Object> response = new HashMap<>();
            response.put("totalTokens", stats[0]);
            response.put("expiredTokens", stats[1]);
            response.put("activeTokens", stats[0] - stats[1]);
            response.put("message", String.format("Total: %d, Active: %d, Expired: %d", 
                                                 stats[0], stats[0] - stats[1], stats[1]));
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to get token statistics: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Manually trigger cleanup of expired tokens
     */
    @PostMapping("/cleanup")
    public ResponseEntity<Map<String, Object>> manualCleanup() {
        try {
            long deletedCount = tokenCleanupScheduler.manualCleanup();
            
            Map<String, Object> response = new HashMap<>();
            response.put("deletedTokens", deletedCount);
            response.put("message", String.format("Successfully cleaned up %d expired tokens", deletedCount));
            
            // Get updated statistics
            long[] stats = tokenCleanupScheduler.getTokenStatistics();
            response.put("remainingTokens", stats[0]);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to cleanup tokens: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Get token cleanup status and next scheduled run info
     */
    @GetMapping("/cleanup-status")
    public ResponseEntity<Map<String, Object>> getCleanupStatus() {
        try {
            long[] stats = tokenCleanupScheduler.getTokenStatistics();
            
            Map<String, Object> response = new HashMap<>();
            response.put("scheduledCleanup", "Every hour at minute 0");
            response.put("cronExpression", "0 0 * * * ?");
            response.put("currentStats", Map.of(
                "totalTokens", stats[0],
                "activeTokens", stats[0] - stats[1],
                "expiredTokens", stats[1]
            ));
            response.put("cleanupEnabled", true);
            response.put("message", stats[1] > 0 ? 
                        String.format("⚠️ %d expired tokens pending cleanup", stats[1]) :
                        "✅ No expired tokens found");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to get cleanup status: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }
}