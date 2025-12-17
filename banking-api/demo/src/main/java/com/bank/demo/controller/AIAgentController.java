package com.bank.demo.controller;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Map;
import java.util.UUID;
import java.util.Arrays;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import com.bank.demo.model.CustomUserDetails;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.User;
import com.bank.demo.repository.transactionRepository;
import com.bank.demo.repository.Userepository;
import com.bank.demo.service.AccountService;
import com.bank.demo.service.SecurityLogAnalysisService;

import jakarta.servlet.http.HttpServletRequest;

@RestController
@RequestMapping("/api/ai")
@CrossOrigin(origins = "*")
public class AIAgentController {

    @Autowired
    private transactionRepository transactionRepository;
    
    @Autowired
    private Userepository userRepository;
    
    @Autowired
    private AccountService accountService;
    
    @Autowired
    private SecurityLogAnalysisService securityLogAnalysisService;
    
    private final RestTemplate restTemplate = new RestTemplate();
    private final String AI_API_BASE_URL = "http://localhost:5001/api";

    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chatWithAI(
            @RequestBody Map<String, Object> request,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        
        try {
            // Get user information
            User user = userRepository.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));
            
            // Prepare request for AI agent
            Map<String, Object> aiRequest = new HashMap<>();
            aiRequest.put("message", request.get("message"));
            aiRequest.put("user_id", user.getId().toString());
            aiRequest.put("user_role", user.getRole().toString().toLowerCase());
            aiRequest.put("location", request.getOrDefault("location", "toronto"));
            
            // Add user context
            aiRequest.put("preferences", Map.of(
                "currency", "CAD",
                "language", "en"
            ));

            // Forward request to AI agent
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(aiRequest, headers);
            
            ResponseEntity<Map> aiResponse = restTemplate.exchange(
                AI_API_BASE_URL + "/chat",
                HttpMethod.POST,
                entity,
                Map.class
            );

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("response", aiResponse.getBody().get("response"));
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            response.put("user_context", Map.of(
                "role", user.getRole(),
                "name", user.getFirstName() + " " + user.getLastName()
            ));

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Failed to connect with AI agent: " + e.getMessage());
            errorResponse.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    @PostMapping("/financial-advice")
    public ResponseEntity<Map<String, Object>> getFinancialAdvice(
            @RequestBody Map<String, Object> request,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        
        try {
            // Get user information
            User user = userRepository.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));

            // Get user's recent transactions for analysis
            List<Transaction> recentTransactions = transactionRepository
                .findByUserIdOrderByCreatedAtDesc(UUID.fromString(user.getId().toString()))
                .stream()
                .limit(50)
                .collect(Collectors.toList());

            // Calculate spending data
            Map<String, Double> spendingData = calculateSpendingData(recentTransactions);

            // Prepare request for AI agent
            Map<String, Object> aiRequest = new HashMap<>();
            aiRequest.put("user_id", user.getId().toString());
            aiRequest.put("location", request.getOrDefault("location", "toronto"));
            aiRequest.put("spending_data", spendingData);
            aiRequest.put("category", request.getOrDefault("category", "grocery"));
            aiRequest.put("target_reduction", request.get("target_reduction"));
            
            // Add transaction history context
            aiRequest.put("transaction_history", recentTransactions.stream()
                .map(t -> Map.of(
                    "amount", t.getAmount(),
                    "description", t.getDescription(),
                    "type", t.getTransactionType(),
                    "date", t.getCreatedAt()
                ))
                .collect(Collectors.toList()));

            // Forward request to AI agent
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(aiRequest, headers);
            
            ResponseEntity<Map> aiResponse = restTemplate.exchange(
                AI_API_BASE_URL + "/user/financial-advice",
                HttpMethod.POST,
                entity,
                Map.class
            );

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("advice", aiResponse.getBody().get("advice"));
            response.put("spending_analysis", Map.of(
                "total_transactions", recentTransactions.size(),
                "spending_data", spendingData,
                "analysis_period", "last_30_days"
            ));
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Failed to get financial advice: " + e.getMessage());
            errorResponse.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    @PostMapping("/security-analysis")
    public ResponseEntity<Map<String, Object>> securityAnalysis(
            @RequestBody Map<String, Object> request,
            @AuthenticationPrincipal CustomUserDetails userDetails,
            HttpServletRequest httpRequest) {
        
        try {
            // Get user information
            User user = userRepository.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));

            // Check if user has admin role
            if (!user.getRole().toString().equals("ADMIN")) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("success", false);
                errorResponse.put("error", "Security analysis only available for admin users");
                errorResponse.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                
                return ResponseEntity.status(403).body(errorResponse);
            }

            // Get suspicious transactions for analysis
            OffsetDateTime oneDayAgo = OffsetDateTime.now().minusDays(1);
            List<Transaction> suspiciousTransactions = transactionRepository
                .findSuspiciousTransactions(oneDayAgo);

            // === ENHANCED SECURITY ANALYSIS ===
            
            // 1. Analyze authentication logs for system-wide threats
            SecurityLogAnalysisService.SystemSecurityOverview systemOverview = 
                securityLogAnalysisService.getSystemSecurityOverview(7); // Last 7 days
            
            // 2. If suspicious transactions found, analyze specific user security
            Map<String, Object> userSecurityAnalysis = new HashMap<>();
            if (!suspiciousTransactions.isEmpty()) {
                Transaction latestSuspicious = suspiciousTransactions.get(0);
                
                // Find the user associated with this transaction
                User suspiciousUser = null;
                try {
                    // Get user from transaction through account relationship
                    if (latestSuspicious.getFromAccount() != null) {
                        suspiciousUser = latestSuspicious.getFromAccount().getUser();
                    } else if (latestSuspicious.getToAccount() != null) {
                        suspiciousUser = latestSuspicious.getToAccount().getUser();
                    }
                } catch (Exception e) {
                    System.err.println("Error finding user from transaction: " + e.getMessage());
                }
                
                if (suspiciousUser != null) {
                    SecurityLogAnalysisService.SecurityAnalysisResult userAnalysis = 
                        securityLogAnalysisService.analyzeUserSecurity(
                            suspiciousUser.getId().toString(),
                            suspiciousUser.getEmail(),
                            14  // Last 14 days
                        );
                    
                    userSecurityAnalysis.put("analyzed_user", suspiciousUser.getEmail());
                    userSecurityAnalysis.put("threat_level", userAnalysis.threatLevel);
                    userSecurityAnalysis.put("summary", userAnalysis.summary);
                    userSecurityAnalysis.put("login_attempts", userAnalysis.totalLoginAttempts);
                    userSecurityAnalysis.put("failed_logins", userAnalysis.failedLogins);
                    userSecurityAnalysis.put("failure_rate", String.format("%.1f%%", userAnalysis.loginFailureRate * 100));
                    userSecurityAnalysis.put("unique_ips", userAnalysis.uniqueIPAddresses);
                    userSecurityAnalysis.put("unique_devices", userAnalysis.uniqueUserAgents);
                    userSecurityAnalysis.put("security_threats", userAnalysis.threats);
                    userSecurityAnalysis.put("risk_factors", userAnalysis.riskFactors);
                    userSecurityAnalysis.put("recommendations", userAnalysis.recommendations);
                }
            }

            // 3. Prepare comprehensive transaction data for AI analysis
            Map<String, Object> transactionData = null;
            if (!suspiciousTransactions.isEmpty()) {
                Transaction latestSuspicious = suspiciousTransactions.get(0);
                transactionData = new HashMap<>();
                transactionData.put("amount", latestSuspicious.getAmount());
                transactionData.put("timestamp", latestSuspicious.getCreatedAt());
                transactionData.put("merchant_type", latestSuspicious.getDescription());
                transactionData.put("transaction_id", latestSuspicious.getTransactionId());
                transactionData.put("transaction_type", latestSuspicious.getTransactionType());
                transactionData.put("account_from", latestSuspicious.getFromAccount() != null ? 
                    latestSuspicious.getFromAccount().getAccountNumber() : "unknown");
                transactionData.put("account_to", latestSuspicious.getToAccount() != null ? 
                    latestSuspicious.getToAccount().getAccountNumber() : "unknown");
            }

            // 4. Prepare enhanced request for AI agent with security context
            Map<String, Object> aiRequest = new HashMap<>();
            aiRequest.put("user_id", user.getId().toString());
            aiRequest.put("location", request.getOrDefault("location", "toronto"));
            aiRequest.put("transaction_data", transactionData);
            
            // Include comprehensive security context
            Map<String, Object> systemOverviewMap = new HashMap<>();
            systemOverviewMap.put("total_events", systemOverview.totalEvents);
            systemOverviewMap.put("active_users", systemOverview.activeUsers);
            systemOverviewMap.put("total_failed_attempts", systemOverview.totalFailedAttempts);
            systemOverviewMap.put("system_failure_rate", String.format("%.2f%%", systemOverview.systemFailureRate * 100));
            systemOverviewMap.put("high_risk_ips", systemOverview.highRiskIPs);
            systemOverviewMap.put("suspicious_ips", systemOverview.suspiciousIPs);
            systemOverviewMap.put("compromised_accounts", systemOverview.potentiallyCompromisedAccounts);
            systemOverviewMap.put("attack_patterns", systemOverview.attackPatterns);
            
            Map<String, Object> securityContext = new HashMap<>();
            securityContext.put("system_overview", systemOverviewMap);
            securityContext.put("user_analysis", userSecurityAnalysis);
            securityContext.put("analysis_scope", "comprehensive_security_audit");
            securityContext.put("data_sources", Arrays.asList("transaction_logs", "authentication_logs", "user_behavior"));
            
            aiRequest.put("security_context", securityContext);

            // 5. Forward request to AI agent
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(aiRequest, headers);
            
            ResponseEntity<Map> aiResponse = restTemplate.exchange(
                AI_API_BASE_URL + "/admin/security-analysis",
                HttpMethod.POST,
                entity,
                Map.class
            );

            // 6. Prepare comprehensive response
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("ai_analysis", aiResponse.getBody().get("analysis"));
            
            // Enhanced system data with security insights
            Map<String, Object> systemOverviewAnalysis = new HashMap<>();
            systemOverviewAnalysis.put("threat_level", determineThreatLevel(systemOverview));
            systemOverviewAnalysis.put("total_events_analyzed", systemOverview.totalEvents);
            systemOverviewAnalysis.put("active_users", systemOverview.activeUsers);
            systemOverviewAnalysis.put("system_failure_rate", String.format("%.2f%%", systemOverview.systemFailureRate * 100));
            systemOverviewAnalysis.put("days_analyzed", systemOverview.daysAnalyzed);
            systemOverviewAnalysis.put("high_risk_indicators", systemOverview.highRiskIPs.size() + systemOverview.suspiciousIPs.size());
            systemOverviewAnalysis.put("potential_compromises", systemOverview.potentiallyCompromisedAccounts.size());
            systemOverviewAnalysis.put("attack_patterns_detected", systemOverview.attackPatterns.size());
            
            Map<String, Object> transactionAnalysis = new HashMap<>();
            transactionAnalysis.put("suspicious_transactions_count", suspiciousTransactions.size());
            transactionAnalysis.put("latest_suspicious", transactionData != null ? transactionData : "none");
            transactionAnalysis.put("total_users_monitored", userRepository.count());
            transactionAnalysis.put("monitoring_active", true);
            
            Map<String, Object> integrationStatus = new HashMap<>();
            integrationStatus.put("auth_logs_analyzed", systemOverview.totalEvents > 0);
            integrationStatus.put("transaction_monitoring", !suspiciousTransactions.isEmpty());
            integrationStatus.put("ai_agent_connected", aiResponse.getStatusCode().is2xxSuccessful());
            integrationStatus.put("comprehensive_analysis", true);
            
            Map<String, Object> securityAnalysis = new HashMap<>();
            securityAnalysis.put("system_overview", systemOverviewAnalysis);
            securityAnalysis.put("user_specific_analysis", userSecurityAnalysis);
            securityAnalysis.put("transaction_analysis", transactionAnalysis);
            securityAnalysis.put("recommendations", generateSystemRecommendations(systemOverview, userSecurityAnalysis));
            securityAnalysis.put("integration_status", integrationStatus);
            
            response.put("security_analysis", securityAnalysis);
            
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Failed to perform comprehensive security analysis: " + e.getMessage());
            errorResponse.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            errorResponse.put("details", "Check authentication logs and ensure AI agent is running");
            
            e.printStackTrace(); // For debugging
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    @GetMapping("/user/spending-summary")
    public ResponseEntity<Map<String, Object>> getUserSpendingSummary(
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        
        try {
            // Get user information
            User user = userRepository.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));

            // Get user's recent transactions
            List<Transaction> recentTransactions = transactionRepository
                .findByUserIdOrderByCreatedAtDesc(UUID.fromString(user.getId().toString()))
                .stream()
                .limit(100)
                .collect(Collectors.toList());

            // Calculate spending summary
            Map<String, Double> spendingData = calculateSpendingData(recentTransactions);
            
            Double totalSpending = recentTransactions.stream()
                .mapToDouble(t -> t.getAmount().abs().doubleValue())
                .sum();

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("spending_summary", Map.of(
                "total_spending", totalSpending,
                "transaction_count", recentTransactions.size(),
                "spending_by_period", spendingData,
                "average_transaction", totalSpending / Math.max(recentTransactions.size(), 1)
            ));
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Failed to get spending summary: " + e.getMessage());
            errorResponse.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        try {
            // Check AI agent health
            ResponseEntity<Map> aiHealth = restTemplate.getForEntity(
                AI_API_BASE_URL + "/health", 
                Map.class
            );

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("status", "healthy");
            response.put("ai_agent_status", aiHealth.getBody());
            response.put("database_status", "connected");
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("status", "unhealthy");
            response.put("error", e.getMessage());
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));

            return ResponseEntity.status(500).body(response);
        }
    }

    private Map<String, Double> calculateSpendingData(List<Transaction> transactions) {
        Map<String, Double> spendingData = new HashMap<>();
        
        // Group transactions by week
        int weekCount = 1;
        double weekTotal = 0.0;
        int transactionCount = 0;
        
        for (Transaction transaction : transactions) {
            if (transaction.getAmount().compareTo(BigDecimal.ZERO) < 0) { // Outgoing transactions
                weekTotal += transaction.getAmount().abs().doubleValue();
                transactionCount++;
                
                if (transactionCount % 10 == 0) { // Every 10 transactions = 1 week (approximation)
                    spendingData.put("week" + weekCount, weekTotal);
                    weekCount++;
                    weekTotal = 0.0;
                    
                    if (weekCount > 4) break; // Only last 4 weeks
                }
            }
        }
        
        // Add remaining transactions as the current week
        if (weekTotal > 0 && weekCount <= 4) {
            spendingData.put("week" + weekCount, weekTotal);
        }
        
        return spendingData;
    }
    
    // === SECURITY ANALYSIS HELPER METHODS ===
    
    /**
     * Determines overall system threat level based on security overview
     */
    private String determineThreatLevel(SecurityLogAnalysisService.SystemSecurityOverview overview) {
        int riskScore = 0;
        
        // Calculate risk based on various factors
        if (overview.systemFailureRate > 0.3) riskScore += 3;  // High failure rate
        else if (overview.systemFailureRate > 0.15) riskScore += 2;  // Medium failure rate
        else if (overview.systemFailureRate > 0.05) riskScore += 1;  // Low failure rate
        
        if (overview.highRiskIPs.size() > 5) riskScore += 3;
        else if (overview.highRiskIPs.size() > 2) riskScore += 2;
        else if (overview.highRiskIPs.size() > 0) riskScore += 1;
        
        if (overview.suspiciousIPs.size() > 3) riskScore += 2;
        else if (overview.suspiciousIPs.size() > 0) riskScore += 1;
        
        if (overview.potentiallyCompromisedAccounts.size() > 2) riskScore += 3;
        else if (overview.potentiallyCompromisedAccounts.size() > 0) riskScore += 2;
        
        if (overview.attackPatterns.size() > 3) riskScore += 3;
        else if (overview.attackPatterns.size() > 1) riskScore += 2;
        else if (overview.attackPatterns.size() > 0) riskScore += 1;
        
        // Determine threat level
        if (riskScore >= 10) return "CRITICAL";
        else if (riskScore >= 7) return "HIGH";
        else if (riskScore >= 4) return "MEDIUM";
        else if (riskScore >= 1) return "LOW";
        else return "MINIMAL";
    }
    
    /**
     * Generate system-wide security recommendations
     */
    private List<String> generateSystemRecommendations(
            SecurityLogAnalysisService.SystemSecurityOverview systemOverview,
            Map<String, Object> userSecurityAnalysis) {
        
        List<String> recommendations = new ArrayList<>();
        
        // System-wide recommendations
        if (systemOverview.systemFailureRate > 0.2) {
            recommendations.add("🚨 URGENT: High system failure rate detected (" + 
                String.format("%.1f%%", systemOverview.systemFailureRate * 100) + 
                "). Investigate potential brute force attacks.");
        }
        
        if (!systemOverview.highRiskIPs.isEmpty()) {
            recommendations.add("🔒 Block or monitor high-risk IP addresses: " + 
                systemOverview.highRiskIPs.size() + " IPs showing excessive activity");
        }
        
        if (!systemOverview.suspiciousIPs.isEmpty()) {
            recommendations.add("🌍 Review geographic access patterns for suspicious IPs: " + 
                String.join(", ", systemOverview.suspiciousIPs.subList(0, Math.min(3, systemOverview.suspiciousIPs.size()))));
        }
        
        if (!systemOverview.potentiallyCompromisedAccounts.isEmpty()) {
            recommendations.add("👤 PRIORITY: Investigate potentially compromised accounts (" + 
                systemOverview.potentiallyCompromisedAccounts.size() + " accounts flagged)");
            recommendations.add("📧 Send security notifications to affected users immediately");
        }
        
        if (!systemOverview.attackPatterns.isEmpty()) {
            recommendations.add("⚡ Coordinated attack patterns detected - implement enhanced monitoring");
            recommendations.add("🛡️ Consider temporary IP blocking for sources showing attack behavior");
        }
        
        // User-specific recommendations if available
        if (!userSecurityAnalysis.isEmpty()) {
            String threatLevel = (String) userSecurityAnalysis.get("threat_level");
            String analyzedUser = (String) userSecurityAnalysis.get("analyzed_user");
            
            if ("CRITICAL".equals(threatLevel) || "HIGH".equals(threatLevel)) {
                recommendations.add("🚨 IMMEDIATE: User " + analyzedUser + " shows " + threatLevel + 
                    " threat level - suspend account pending investigation");
            }
            
            @SuppressWarnings("unchecked")
            List<String> userThreats = (List<String>) userSecurityAnalysis.get("security_threats");
            if (userThreats != null && !userThreats.isEmpty()) {
                recommendations.add("📋 User-specific threats detected for " + analyzedUser + 
                    ": " + userThreats.size() + " security concerns");
            }
        }
        
        // General security recommendations
        if (systemOverview.totalFailedAttempts > 100) {
            recommendations.add("🔐 Implement stricter account lockout policies");
            recommendations.add("📱 Enable multi-factor authentication for all high-risk accounts");
        }
        
        if (systemOverview.activeUsers > 50 && systemOverview.totalEvents < systemOverview.activeUsers * 2) {
            recommendations.add("📊 Monitor for unusual periods of low activity (potential system compromise)");
        }
        
        // Default recommendations if no specific threats
        if (recommendations.isEmpty()) {
            recommendations.add("✅ System security appears normal - continue regular monitoring");
            recommendations.add("🔄 Maintain current security protocols and user education");
            recommendations.add("📈 Consider implementing additional behavioral analytics");
        }
        
        return recommendations;
    }
    
    /**
     * Analyze if a user account shows signs of compromise based on transaction patterns
     */
    private Map<String, Object> analyzeAccountCompromiseIndicators(User user, List<Transaction> recentTransactions) {
        Map<String, Object> analysis = new HashMap<>();
        List<String> compromiseIndicators = new ArrayList<>();
        
        try {
            // Analyze transaction patterns for compromise indicators
            if (recentTransactions.size() > 20) {
                
                // 1. Check for unusual transaction amounts
                double avgAmount = recentTransactions.stream()
                    .mapToDouble(t -> t.getAmount().abs().doubleValue())
                    .average().orElse(0.0);
                
                long unusualAmounts = recentTransactions.stream()
                    .filter(t -> t.getAmount().abs().doubleValue() > avgAmount * 3)
                    .count();
                
                if (unusualAmounts > 3) {
                    compromiseIndicators.add("Unusual transaction amounts detected (" + unusualAmounts + " transactions)");
                }
                
                // 2. Check for rapid successive transactions
                // Sort transactions by timestamp and check for rapid sequences
                List<Transaction> sortedTransactions = recentTransactions.stream()
                    .sorted((a, b) -> a.getCreatedAt().compareTo(b.getCreatedAt()))
                    .collect(Collectors.toList());
                
                int rapidSequences = 0;
                for (int i = 0; i < sortedTransactions.size() - 2; i++) {
                    OffsetDateTime first = sortedTransactions.get(i).getCreatedAt();
                    OffsetDateTime third = sortedTransactions.get(i + 2).getCreatedAt();
                    
                    if (first.plusMinutes(5).isAfter(third)) {
                        rapidSequences++;
                    }
                }
                
                if (rapidSequences > 2) {
                    compromiseIndicators.add("Rapid transaction sequences detected (" + rapidSequences + " sequences)");
                }
                
                // 3. Check for transactions at unusual times (2-5 AM)
                long nightTransactions = recentTransactions.stream()
                    .filter(t -> {
                        int hour = t.getCreatedAt().getHour();
                        return hour >= 2 && hour <= 5;
                    })
                    .count();
                
                if (nightTransactions > 3) {
                    compromiseIndicators.add("Unusual nighttime activity (" + nightTransactions + " transactions between 2-5 AM)");
                }
            }
            
            // Determine compromise probability
            String compromiseProbability;
            if (compromiseIndicators.size() >= 3) {
                compromiseProbability = "HIGH";
            } else if (compromiseIndicators.size() >= 2) {
                compromiseProbability = "MEDIUM";
            } else if (compromiseIndicators.size() >= 1) {
                compromiseProbability = "LOW";
            } else {
                compromiseProbability = "MINIMAL";
            }
            
            analysis.put("compromise_probability", compromiseProbability);
            analysis.put("indicators", compromiseIndicators);
            analysis.put("transactions_analyzed", recentTransactions.size());
            analysis.put("analysis_timeframe", "recent_activity");
            
        } catch (Exception e) {
            analysis.put("error", "Failed to analyze account compromise indicators: " + e.getMessage());
        }
        
        return analysis;
    }
}