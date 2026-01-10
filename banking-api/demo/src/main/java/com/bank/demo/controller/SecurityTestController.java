package com.bank.demo.controller;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import com.bank.demo.model.CustomUserDetails;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.User;
import com.bank.demo.repository.transactionRepository;
import com.bank.demo.repository.Userepository;
import com.bank.demo.service.SecurityLogAnalysisService;
import com.bank.demo.service.AuthLoggingService;
import com.bank.demo.utils.AsyncAuthLogWriter;

import jakarta.servlet.http.HttpServletRequest;

@RestController
@RequestMapping("/api/security-test")
@CrossOrigin(origins = "*")
public class SecurityTestController {

    @Autowired
    private SecurityLogAnalysisService securityLogAnalysisService;
    
    @Autowired
    private transactionRepository transactionRepository;
    
    @Autowired
    private Userepository userRepository;
    
    @Autowired
    private AuthLoggingService authLoggingService;
    
    @Autowired
    private AsyncAuthLogWriter asyncAuthLogWriter;

    @GetMapping("/comprehensive-demo")
    public ResponseEntity<Map<String, Object>> comprehensiveSecurityDemo(
            @AuthenticationPrincipal CustomUserDetails userDetails,
            HttpServletRequest httpRequest) {
        
        try {
            // Get user information
            User user = userRepository.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));

            // 1. Generate some test authentication logs
            generateTestAuthLogs(user, httpRequest);
            
            // 2. Get suspicious transactions
            OffsetDateTime oneDayAgo = OffsetDateTime.now().minusDays(1);
            List<Transaction> suspiciousTransactions = transactionRepository.findSuspiciousTransactions(oneDayAgo);
            
            // 3. Perform comprehensive security analysis
            SecurityLogAnalysisService.SystemSecurityOverview systemOverview = 
                securityLogAnalysisService.getSystemSecurityOverview(7);
                
            SecurityLogAnalysisService.SecurityAnalysisResult userAnalysis = 
                securityLogAnalysisService.analyzeUserSecurity(
                    user.getId().toString(),
                    user.getEmail(),
                    14
                );

            // 4. Analyze transaction patterns for compromise indicators
            List<Transaction> userTransactions = transactionRepository
                .findByUserIdOrderByCreatedAtDesc(user.getId())
                .stream()
                .limit(50)
                .collect(Collectors.toList());
                
            Map<String, Object> compromiseAnalysis = analyzeAccountCompromiseIndicators(user, userTransactions);

            // 5. Prepare comprehensive demo response
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("demo_type", "comprehensive_security_analysis");
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            // System Security Overview
            Map<String, Object> systemSecurityMap = new HashMap<>();
            systemSecurityMap.put("threat_level", determineThreatLevel(systemOverview));
            systemSecurityMap.put("total_events", systemOverview.totalEvents);
            systemSecurityMap.put("active_users", systemOverview.activeUsers);
            systemSecurityMap.put("total_logins", systemOverview.totalLogins);
            systemSecurityMap.put("failed_attempts", systemOverview.totalFailedAttempts);
            systemSecurityMap.put("failure_rate", String.format("%.2f%%", systemOverview.systemFailureRate * 100));
            systemSecurityMap.put("high_risk_ips", systemOverview.highRiskIPs);
            systemSecurityMap.put("suspicious_ips", systemOverview.suspiciousIPs);
            systemSecurityMap.put("compromised_accounts", systemOverview.potentiallyCompromisedAccounts);
            systemSecurityMap.put("attack_patterns", systemOverview.attackPatterns);
            systemSecurityMap.put("days_analyzed", systemOverview.daysAnalyzed);
            
            response.put("system_security", systemSecurityMap);
            
            // User Security Analysis
            Map<String, Object> userSecurityMap = new HashMap<>();
            userSecurityMap.put("analyzed_user", userAnalysis.username);
            userSecurityMap.put("threat_level", userAnalysis.threatLevel);
            userSecurityMap.put("summary", userAnalysis.summary);
            userSecurityMap.put("login_attempts", userAnalysis.totalLoginAttempts);
            userSecurityMap.put("successful_logins", userAnalysis.successfulLogins);
            userSecurityMap.put("failed_logins", userAnalysis.failedLogins);
            userSecurityMap.put("failure_rate", String.format("%.1f%%", userAnalysis.loginFailureRate * 100));
            userSecurityMap.put("unique_ips", userAnalysis.uniqueIPAddresses);
            userSecurityMap.put("unique_devices", userAnalysis.uniqueUserAgents);
            userSecurityMap.put("security_threats", userAnalysis.threats);
            userSecurityMap.put("risk_factors", userAnalysis.riskFactors);
            userSecurityMap.put("recommendations", userAnalysis.recommendations);
            userSecurityMap.put("days_analyzed", userAnalysis.daysAnalyzed);
            
            response.put("user_security", userSecurityMap);
            
            // Transaction Analysis
            Map<String, Object> transactionAnalysisMap = new HashMap<>();
            transactionAnalysisMap.put("suspicious_transactions", suspiciousTransactions.stream()
                .limit(5)
                .map(this::transactionToMap)
                .collect(Collectors.toList()));
            transactionAnalysisMap.put("user_transactions_analyzed", userTransactions.size());
            transactionAnalysisMap.put("compromise_analysis", compromiseAnalysis);
            transactionAnalysisMap.put("total_suspicious_count", suspiciousTransactions.size());
            
            response.put("transaction_analysis", transactionAnalysisMap);
            
            // Integration Status
            Map<String, Object> integrationStatusMap = new HashMap<>();
            integrationStatusMap.put("auth_logs_available", systemOverview.totalEvents > 0);
            integrationStatusMap.put("transaction_monitoring", !suspiciousTransactions.isEmpty());
            integrationStatusMap.put("user_analysis_complete", !userAnalysis.threats.isEmpty() || userAnalysis.threatLevel.equals("LOW"));
            integrationStatusMap.put("system_analysis_complete", systemOverview.totalEvents > 0);
            integrationStatusMap.put("comprehensive_data", true);
            
            response.put("integration_status", integrationStatusMap);
            
            // Security Insights Summary
            List<String> securityInsights = new ArrayList<>();
            
            if (!systemOverview.potentiallyCompromisedAccounts.isEmpty()) {
                securityInsights.add("🚨 " + systemOverview.potentiallyCompromisedAccounts.size() + " potentially compromised accounts detected");
            }
            
            if (systemOverview.systemFailureRate > 0.2) {
                securityInsights.add("⚠️ High system failure rate: " + String.format("%.1f%%", systemOverview.systemFailureRate * 100));
            }
            
            if (!userAnalysis.threats.isEmpty()) {
                securityInsights.add("👤 User-specific threats: " + userAnalysis.threats.size() + " concerns for " + userAnalysis.username);
            }
            
            if (!systemOverview.attackPatterns.isEmpty()) {
                securityInsights.add("🔍 Attack patterns detected: " + systemOverview.attackPatterns.size() + " coordinated attempts");
            }
            
            if (!suspiciousTransactions.isEmpty()) {
                securityInsights.add("💰 Financial anomalies: " + suspiciousTransactions.size() + " suspicious transactions");
            }
            
            if (securityInsights.isEmpty()) {
                securityInsights.add("✅ No immediate security threats detected");
                securityInsights.add("🔄 System operating within normal parameters");
            }
            
            response.put("security_insights", securityInsights);
            
            // Demonstration Data
            Map<String, Object> demonstrationMap = new HashMap<>();
            demonstrationMap.put("purpose", "Showcase comprehensive security analysis integrating authentication logs and transaction monitoring");
            demonstrationMap.put("data_sources", Arrays.asList("Authentication logs", "Transaction database", "User behavior analytics"));
            demonstrationMap.put("analysis_types", Arrays.asList("System overview", "User-specific analysis", "Transaction patterns", "Compromise indicators"));
            demonstrationMap.put("integration_features", Arrays.asList("Real-time log analysis", "Pattern detection", "Risk scoring", "Automated recommendations"));
            demonstrationMap.put("test_data_generated", true);
            
            response.put("demonstration", demonstrationMap);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Failed to perform comprehensive security demo: " + e.getMessage());
            errorResponse.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            e.printStackTrace();
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
    
    @PostMapping("/generate-test-scenario")
    public ResponseEntity<Map<String, Object>> generateTestScenario(
            @RequestBody Map<String, Object> request,
            @AuthenticationPrincipal CustomUserDetails userDetails,
            HttpServletRequest httpRequest) {
        
        try {
            User user = userRepository.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));
            
            String scenario = (String) request.getOrDefault("scenario", "normal");
            
            switch (scenario.toLowerCase()) {
                case "brute_force":
                    generateBruteForceScenario(user, httpRequest);
                    break;
                case "suspicious_geography":
                    generateSuspiciousGeographyScenario(user, httpRequest);
                    break;
                case "account_takeover":
                    generateAccountTakeoverScenario(user, httpRequest);
                    break;
                case "multiple_devices":
                    generateMultipleDevicesScenario(user, httpRequest);
                    break;
                default:
                    generateNormalActivityScenario(user, httpRequest);
            }
            
            // Wait a moment for logs to be written
            Thread.sleep(2000);
            
            // Analyze the generated scenario
            SecurityLogAnalysisService.SecurityAnalysisResult analysis = 
                securityLogAnalysisService.analyzeUserSecurity(
                    user.getId().toString(),
                    user.getEmail(),
                    1 // Just today
                );

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("scenario_generated", scenario);
            response.put("analysis_result", Map.of(
                "threat_level", analysis.threatLevel,
                "summary", analysis.summary,
                "threats_detected", analysis.threats,
                "risk_factors", analysis.riskFactors,
                "recommendations", analysis.recommendations
            ));
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", "Failed to generate test scenario: " + e.getMessage());
            
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
    
    @GetMapping("/log-buffer-status")
    public ResponseEntity<Map<String, Object>> getLogBufferStatus() {
        Map<String, Object> response = new HashMap<>();
        response.put("buffer_size", asyncAuthLogWriter.getBufferSize());
        response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        response.put("status", "active");
        
        return ResponseEntity.ok(response);
    }
    
    // === PRIVATE HELPER METHODS ===
    
    private void generateTestAuthLogs(User user, HttpServletRequest request) {
        // Generate some normal activity
        authLoggingService.logCustomEvent("LOGIN_SUCCESS", user.getEmail(), true, 
            "Normal login activity", request);
        authLoggingService.logCustomEvent("AUTHENTICATION_SUCCESS", user.getEmail(), true, 
            "JWT authentication successful", request);
        
        // Generate some suspicious activity
        authLoggingService.logCustomEvent("LOGIN_FAILED", user.getEmail(), false, 
            "Failed login attempt - wrong password", request);
        authLoggingService.logCustomEvent("LOGIN_FAILED", user.getEmail(), false, 
            "Failed login attempt - account locked", request);
    }
    
    private void generateBruteForceScenario(User user, HttpServletRequest request) {
        // Generate multiple failed attempts in quick succession
        for (int i = 0; i < 8; i++) {
            authLoggingService.logCustomEvent("LOGIN_FAILED", user.getEmail(), false, 
                "Brute force attempt #" + (i + 1), request);
        }
        // One successful login after many failures
        authLoggingService.logCustomEvent("LOGIN_SUCCESS", user.getEmail(), true, 
            "Login successful after multiple failures", request);
    }
    
    private void generateSuspiciousGeographyScenario(User user, HttpServletRequest request) {
        // Simulate logins from different geographic locations (mock IPs)
        String[] suspiciousIPs = {"91.198.22.70", "203.142.99.12", "46.23.104.45"};
        
        for (String ip : suspiciousIPs) {
            authLoggingService.logCustomEvent("LOGIN_SUCCESS", user.getEmail(), true, 
                "Login from suspicious geography: " + ip, request);
        }
    }
    
    private void generateAccountTakeoverScenario(User user, HttpServletRequest request) {
        // Multiple failed attempts
        for (int i = 0; i < 5; i++) {
            authLoggingService.logCustomEvent("LOGIN_FAILED", user.getEmail(), false, 
                "Account takeover attempt - wrong credentials", request);
        }
        
        // Successful login with different user agent
        authLoggingService.logCustomEvent("LOGIN_SUCCESS", user.getEmail(), true, 
            "Suspicious successful login with unusual device", request);
        
        // Rapid activity
        authLoggingService.logCustomEvent("AUTHENTICATION_SUCCESS", user.getEmail(), true, 
            "Multiple rapid authentications", request);
        authLoggingService.logCustomEvent("AUTHENTICATION_SUCCESS", user.getEmail(), true, 
            "Unusual activity pattern detected", request);
    }
    
    private void generateMultipleDevicesScenario(User user, HttpServletRequest request) {
        String[] userAgents = {
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        };
        
        for (String agent : userAgents) {
            authLoggingService.logCustomEvent("LOGIN_SUCCESS", user.getEmail(), true, 
                "Login from device: " + agent.substring(0, 30) + "...", request);
        }
    }
    
    private void generateNormalActivityScenario(User user, HttpServletRequest request) {
        // Normal login pattern
        authLoggingService.logCustomEvent("LOGIN_SUCCESS", user.getEmail(), true, 
            "Normal daily login", request);
        authLoggingService.logCustomEvent("AUTHENTICATION_SUCCESS", user.getEmail(), true, 
            "Regular session activity", request);
        authLoggingService.logCustomEvent("LOGOUT_SUCCESS", user.getEmail(), true, 
            "Normal logout", request);
    }
    
    private Map<String, Object> transactionToMap(Transaction transaction) {
        Map<String, Object> map = new HashMap<>();
        map.put("transaction_id", transaction.getTransactionId());
        map.put("amount", transaction.getAmount());
        map.put("description", transaction.getDescription());
        map.put("type", transaction.getTransactionType());
        map.put("status", transaction.getTransactionStatus());
        map.put("created_at", transaction.getCreatedAt());
        map.put("transaction_id", transaction.getTransactionId());
        return map;
    }
    
    private String determineThreatLevel(SecurityLogAnalysisService.SystemSecurityOverview overview) {
        int riskScore = 0;
        
        if (overview.systemFailureRate > 0.3) riskScore += 3;
        else if (overview.systemFailureRate > 0.15) riskScore += 2;
        else if (overview.systemFailureRate > 0.05) riskScore += 1;
        
        if (overview.highRiskIPs.size() > 5) riskScore += 3;
        else if (overview.highRiskIPs.size() > 2) riskScore += 2;
        else if (overview.highRiskIPs.size() > 0) riskScore += 1;
        
        if (overview.potentiallyCompromisedAccounts.size() > 2) riskScore += 3;
        else if (overview.potentiallyCompromisedAccounts.size() > 0) riskScore += 2;
        
        if (riskScore >= 7) return "CRITICAL";
        else if (riskScore >= 5) return "HIGH";
        else if (riskScore >= 3) return "MEDIUM";
        else if (riskScore >= 1) return "LOW";
        else return "MINIMAL";
    }
    
    private Map<String, Object> analyzeAccountCompromiseIndicators(User user, List<Transaction> recentTransactions) {
        Map<String, Object> analysis = new HashMap<>();
        List<String> indicators = new ArrayList<>();
        
        if (recentTransactions.size() > 10) {
            // Check for unusual amounts
            double avgAmount = recentTransactions.stream()
                .mapToDouble(t -> t.getAmount().abs().doubleValue())
                .average().orElse(0.0);
                
            long unusualAmounts = recentTransactions.stream()
                .filter(t -> t.getAmount().abs().doubleValue() > avgAmount * 2)
                .count();
                
            if (unusualAmounts > 2) {
                indicators.add("Unusual transaction amounts detected");
            }
            
            // Check for rapid sequences
            long rapidTransactions = recentTransactions.stream()
                .filter(t -> t.getCreatedAt().isAfter(OffsetDateTime.now().minusHours(1)))
                .count();
                
            if (rapidTransactions > 5) {
                indicators.add("High transaction frequency in short timeframe");
            }
        }
        
        String riskLevel = indicators.size() >= 2 ? "HIGH" : indicators.size() == 1 ? "MEDIUM" : "LOW";
        
        analysis.put("risk_level", riskLevel);
        analysis.put("indicators", indicators);
        analysis.put("transactions_analyzed", recentTransactions.size());
        
        return analysis;
    }
}