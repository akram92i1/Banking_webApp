package com.bank.demo.service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.*;
import java.util.stream.Collectors;
import java.util.regex.Pattern;

import org.springframework.stereotype.Service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class SecurityLogAnalysisService {
    
    private final ObjectMapper objectMapper;
    private static final String LOG_DIR = "logs";
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");
    private static final DateTimeFormatter ISO_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
    
    // Suspicious patterns
    private static final List<String> SUSPICIOUS_COUNTRIES = Arrays.asList(
        "RU", "CN", "KP", "IR", "SY"  // Example suspicious country codes
    );
    
    private static final Pattern TOR_EXIT_PATTERN = Pattern.compile(".*tor.*|.*proxy.*|.*vpn.*", Pattern.CASE_INSENSITIVE);
    private static final Pattern SUSPICIOUS_USER_AGENT_PATTERN = Pattern.compile(".*bot.*|.*crawler.*|.*scanner.*|.*sqlmap.*", Pattern.CASE_INSENSITIVE);
    
    public SecurityLogAnalysisService() {
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * Comprehensive security analysis for a specific user
     */
    public SecurityAnalysisResult analyzeUserSecurity(String userId, String username, int daysBack) {
        SecurityAnalysisResult result = new SecurityAnalysisResult();
        result.userId = userId;
        result.username = username;
        result.analysisTimestamp = LocalDateTime.now();
        result.daysAnalyzed = daysBack;
        
        try {
            // Get logs from the last N days
            List<Map<String, Object>> userLogs = getUserLogsFromPeriod(username, daysBack);
            
            if (userLogs.isEmpty()) {
                result.threatLevel = "LOW";
                result.summary = "No authentication logs found for analysis";
                return result;
            }
            
            // Analyze different security aspects
            analyzeLoginPatterns(userLogs, result);
            analyzeGeographicAnomalies(userLogs, result);
            analyzeSuspiciousIPs(userLogs, result);
            analyzeFailedAttempts(userLogs, result);
            analyzeUserAgentAnomalies(userLogs, result);
            analyzeTimingPatterns(userLogs, result);
            
            // Calculate overall threat level
            calculateOverallThreatLevel(result);
            
            // Generate recommendations
            generateSecurityRecommendations(result);
            
        } catch (Exception e) {
            result.threatLevel = "UNKNOWN";
            result.summary = "Error analyzing security logs: " + e.getMessage();
            result.errors.add("Analysis failed: " + e.getMessage());
        }
        
        return result;
    }
    
    /**
     * Get recent authentication logs for all users (admin overview)
     */
    public SystemSecurityOverview getSystemSecurityOverview(int daysBack) {
        SystemSecurityOverview overview = new SystemSecurityOverview();
        overview.analysisTimestamp = LocalDateTime.now();
        overview.daysAnalyzed = daysBack;
        
        try {
            List<Map<String, Object>> allLogs = getAllLogsFromPeriod(daysBack);
            
            // Analyze system-wide patterns
            analyzeSystemLoginPatterns(allLogs, overview);
            analyzeSystemThreats(allLogs, overview);
            identifyCompromisedAccounts(allLogs, overview);
            analyzeAttackPatterns(allLogs, overview);
            
        } catch (Exception e) {
            overview.errors.add("System analysis failed: " + e.getMessage());
        }
        
        return overview;
    }
    
    // === PRIVATE ANALYSIS METHODS ===
    
    private List<Map<String, Object>> getUserLogsFromPeriod(String username, int daysBack) throws IOException {
        List<Map<String, Object>> userLogs = new ArrayList<>();
        
        LocalDateTime startDate = LocalDateTime.now().minusDays(daysBack);
        LocalDateTime currentDate = LocalDateTime.now();
        
        // Check each day's log file
        for (LocalDateTime date = startDate; date.isBefore(currentDate.plusDays(1)); date = date.plusDays(1)) {
            String dateStr = date.format(DATE_FORMATTER);
            String fileName = LOG_DIR + "/auth_logs_" + dateStr + ".json";
            
            List<Map<String, Object>> dayLogs = readDayLogs(fileName);
            
            // Filter logs for this specific user
            List<Map<String, Object>> userDayLogs = dayLogs.stream()
                .filter(log -> username.equals(log.get("username")))
                .collect(Collectors.toList());
                
            userLogs.addAll(userDayLogs);
        }
        
        return userLogs;
    }
    
    private List<Map<String, Object>> getAllLogsFromPeriod(int daysBack) throws IOException {
        List<Map<String, Object>> allLogs = new ArrayList<>();
        
        LocalDateTime startDate = LocalDateTime.now().minusDays(daysBack);
        LocalDateTime currentDate = LocalDateTime.now();
        
        for (LocalDateTime date = startDate; date.isBefore(currentDate.plusDays(1)); date = date.plusDays(1)) {
            String dateStr = date.format(DATE_FORMATTER);
            String fileName = LOG_DIR + "/auth_logs_" + dateStr + ".json";
            
            List<Map<String, Object>> dayLogs = readDayLogs(fileName);
            allLogs.addAll(dayLogs);
        }
        
        return allLogs;
    }
    
    private List<Map<String, Object>> readDayLogs(String fileName) {
        try {
            File logFile = new File(fileName);
            if (!logFile.exists() || logFile.length() == 0) {
                return new ArrayList<>();
            }
            
            String content = Files.readString(Paths.get(fileName));
            if (content.trim().isEmpty()) {
                return new ArrayList<>();
            }
            
            TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {};
            Map<String, Object> dailyLogsStructure = objectMapper.readValue(content, typeRef);
            
            Object logsObj = dailyLogsStructure.get("logs");
            if (logsObj instanceof List) {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> logs = (List<Map<String, Object>>) logsObj;
                return logs;
            }
            
        } catch (Exception e) {
            System.err.println("Error reading log file " + fileName + ": " + e.getMessage());
        }
        
        return new ArrayList<>();
    }
    
    private void analyzeLoginPatterns(List<Map<String, Object>> logs, SecurityAnalysisResult result) {
        Map<String, Integer> eventCounts = new HashMap<>();
        
        for (Map<String, Object> log : logs) {
            String eventType = (String) log.get("eventType");
            eventCounts.put(eventType, eventCounts.getOrDefault(eventType, 0) + 1);
        }
        
        int totalLogins = eventCounts.getOrDefault("LOGIN_SUCCESS", 0);
        int failedLogins = eventCounts.getOrDefault("LOGIN_FAILED", 0);
        
        result.totalLoginAttempts = totalLogins + failedLogins;
        result.successfulLogins = totalLogins;
        result.failedLogins = failedLogins;
        
        // Calculate failure rate
        if (result.totalLoginAttempts > 0) {
            result.loginFailureRate = (double) failedLogins / result.totalLoginAttempts;
            
            if (result.loginFailureRate > 0.3) {  // More than 30% failures
                result.threats.add("High login failure rate detected: " + String.format("%.1f%%", result.loginFailureRate * 100));
                result.riskFactors.add("LOGIN_FAILURE_RATE");
            }
        }
    }
    
    private void analyzeGeographicAnomalies(List<Map<String, Object>> logs, SecurityAnalysisResult result) {
        Set<String> uniqueIPs = new HashSet<>();
        Set<String> suspiciousCountries = new HashSet<>();
        
        for (Map<String, Object> log : logs) {
            String clientIP = (String) log.get("clientIP");
            if (clientIP != null) {
                uniqueIPs.add(clientIP);
                
                // Simple country detection (in real app, use GeoIP service)
                String country = detectCountryFromIP(clientIP);
                if (SUSPICIOUS_COUNTRIES.contains(country)) {
                    suspiciousCountries.add(country);
                    result.threats.add("Login from suspicious country: " + country + " (IP: " + clientIP + ")");
                    result.riskFactors.add("SUSPICIOUS_GEOGRAPHY");
                }
            }
        }
        
        result.uniqueIPAddresses = uniqueIPs.size();
        
        // Multiple IPs might indicate account sharing or compromise
        if (uniqueIPs.size() > 5) {
            result.threats.add("Multiple IP addresses detected: " + uniqueIPs.size() + " different IPs");
            result.riskFactors.add("MULTIPLE_IPS");
        }
    }
    
    private void analyzeSuspiciousIPs(List<Map<String, Object>> logs, SecurityAnalysisResult result) {
        Map<String, Integer> ipCounts = new HashMap<>();
        Set<String> suspiciousIPs = new HashSet<>();
        
        for (Map<String, Object> log : logs) {
            String clientIP = (String) log.get("clientIP");
            if (clientIP != null) {
                ipCounts.put(clientIP, ipCounts.getOrDefault(clientIP, 0) + 1);
                
                // Check for suspicious IP patterns
                if (isSuspiciousIP(clientIP)) {
                    suspiciousIPs.add(clientIP);
                }
            }
        }
        
        // Check for IPs with many failed attempts
        for (Map.Entry<String, Integer> entry : ipCounts.entrySet()) {
            if (entry.getValue() > 10) {  // More than 10 attempts from same IP
                result.threats.add("High activity from IP: " + entry.getKey() + " (" + entry.getValue() + " attempts)");
                result.riskFactors.add("HIGH_IP_ACTIVITY");
            }
        }
        
        if (!suspiciousIPs.isEmpty()) {
            result.threats.add("Suspicious IP addresses detected: " + String.join(", ", suspiciousIPs));
            result.riskFactors.add("SUSPICIOUS_IPS");
        }
    }
    
    private void analyzeFailedAttempts(List<Map<String, Object>> logs, SecurityAnalysisResult result) {
        List<Map<String, Object>> failedAttempts = logs.stream()
            .filter(log -> "LOGIN_FAILED".equals(log.get("eventType")))
            .sorted((a, b) -> {
                String timeA = (String) a.get("timestamp");
                String timeB = (String) b.get("timestamp");
                try {
                    return LocalDateTime.parse(timeA, ISO_FORMATTER)
                        .compareTo(LocalDateTime.parse(timeB, ISO_FORMATTER));
                } catch (DateTimeParseException e) {
                    return 0;
                }
            })
            .collect(Collectors.toList());
        
        // Check for rapid successive failures (possible brute force)
        if (failedAttempts.size() >= 5) {
            List<LocalDateTime> failureTimes = new ArrayList<>();
            
            for (Map<String, Object> failure : failedAttempts) {
                try {
                    String timestamp = (String) failure.get("timestamp");
                    failureTimes.add(LocalDateTime.parse(timestamp, ISO_FORMATTER));
                } catch (DateTimeParseException e) {
                    // Skip invalid timestamps
                }
            }
            
            // Check for 5+ failures within 15 minutes
            for (int i = 0; i <= failureTimes.size() - 5; i++) {
                LocalDateTime start = failureTimes.get(i);
                LocalDateTime end = failureTimes.get(i + 4);
                
                if (start.plusMinutes(15).isAfter(end)) {
                    result.threats.add("Possible brute force attack detected: 5+ failed attempts within 15 minutes");
                    result.riskFactors.add("BRUTE_FORCE_PATTERN");
                    break;
                }
            }
        }
    }
    
    private void analyzeUserAgentAnomalies(List<Map<String, Object>> logs, SecurityAnalysisResult result) {
        Set<String> userAgents = new HashSet<>();
        Set<String> suspiciousAgents = new HashSet<>();
        
        for (Map<String, Object> log : logs) {
            String userAgent = (String) log.get("userAgent");
            if (userAgent != null) {
                userAgents.add(userAgent);
                
                if (SUSPICIOUS_USER_AGENT_PATTERN.matcher(userAgent).matches()) {
                    suspiciousAgents.add(userAgent);
                }
            }
        }
        
        result.uniqueUserAgents = userAgents.size();
        
        // Multiple user agents might indicate automated tools or compromise
        if (userAgents.size() > 3) {
            result.threats.add("Multiple user agents detected: " + userAgents.size() + " different browsers/devices");
            result.riskFactors.add("MULTIPLE_USER_AGENTS");
        }
        
        if (!suspiciousAgents.isEmpty()) {
            result.threats.add("Suspicious user agents detected: " + String.join(", ", suspiciousAgents));
            result.riskFactors.add("SUSPICIOUS_USER_AGENTS");
        }
    }
    
    private void analyzeTimingPatterns(List<Map<String, Object>> logs, SecurityAnalysisResult result) {
        Map<Integer, Integer> hourlyActivity = new HashMap<>();
        
        for (Map<String, Object> log : logs) {
            try {
                String timestamp = (String) log.get("timestamp");
                LocalDateTime dateTime = LocalDateTime.parse(timestamp, ISO_FORMATTER);
                int hour = dateTime.getHour();
                hourlyActivity.put(hour, hourlyActivity.getOrDefault(hour, 0) + 1);
            } catch (DateTimeParseException e) {
                // Skip invalid timestamps
            }
        }
        
        // Check for unusual time patterns (e.g., activity at 3 AM)
        for (Map.Entry<Integer, Integer> entry : hourlyActivity.entrySet()) {
            int hour = entry.getKey();
            int count = entry.getValue();
            
            if ((hour >= 2 && hour <= 5) && count > 5) {  // Activity between 2-5 AM
                result.threats.add("Unusual login activity detected at " + hour + ":00 (" + count + " attempts)");
                result.riskFactors.add("UNUSUAL_HOURS");
            }
        }
    }
    
    // === SYSTEM ANALYSIS METHODS ===
    
    private void analyzeSystemLoginPatterns(List<Map<String, Object>> allLogs, SystemSecurityOverview overview) {
        Map<String, Integer> eventCounts = new HashMap<>();
        Set<String> activeUsers = new HashSet<>();
        
        for (Map<String, Object> log : allLogs) {
            String eventType = (String) log.get("eventType");
            String username = (String) log.get("username");
            
            eventCounts.put(eventType, eventCounts.getOrDefault(eventType, 0) + 1);
            if (username != null) {
                activeUsers.add(username);
            }
        }
        
        overview.totalEvents = allLogs.size();
        overview.activeUsers = activeUsers.size();
        overview.totalLogins = eventCounts.getOrDefault("LOGIN_SUCCESS", 0);
        overview.totalFailedAttempts = eventCounts.getOrDefault("LOGIN_FAILED", 0);
        
        if (overview.totalLogins + overview.totalFailedAttempts > 0) {
            overview.systemFailureRate = (double) overview.totalFailedAttempts / (overview.totalLogins + overview.totalFailedAttempts);
        }
    }
    
    private void analyzeSystemThreats(List<Map<String, Object>> allLogs, SystemSecurityOverview overview) {
        Map<String, Integer> ipActivityCounts = new HashMap<>();
        Set<String> suspiciousIPs = new HashSet<>();
        
        for (Map<String, Object> log : allLogs) {
            String clientIP = (String) log.get("clientIP");
            if (clientIP != null) {
                ipActivityCounts.put(clientIP, ipActivityCounts.getOrDefault(clientIP, 0) + 1);
                
                if (isSuspiciousIP(clientIP)) {
                    suspiciousIPs.add(clientIP);
                }
            }
        }
        
        // Find IPs with excessive activity
        for (Map.Entry<String, Integer> entry : ipActivityCounts.entrySet()) {
            if (entry.getValue() > 50) {  // More than 50 requests
                overview.highRiskIPs.add(entry.getKey() + " (" + entry.getValue() + " requests)");
            }
        }
        
        overview.suspiciousIPs.addAll(suspiciousIPs);
    }
    
    private void identifyCompromisedAccounts(List<Map<String, Object>> allLogs, SystemSecurityOverview overview) {
        Map<String, List<Map<String, Object>>> userLogs = allLogs.stream()
            .filter(log -> log.get("username") != null)
            .collect(Collectors.groupingBy(log -> (String) log.get("username")));
        
        for (Map.Entry<String, List<Map<String, Object>>> entry : userLogs.entrySet()) {
            String username = entry.getKey();
            List<Map<String, Object>> logs = entry.getValue();
            
            // Quick compromise indicators
            Set<String> ips = logs.stream()
                .map(log -> (String) log.get("clientIP"))
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());
            
            long failedAttempts = logs.stream()
                .filter(log -> "LOGIN_FAILED".equals(log.get("eventType")))
                .count();
            
            // Simple heuristic for potential compromise
            if (ips.size() > 10 || failedAttempts > 20) {
                overview.potentiallyCompromisedAccounts.add(username + " (IPs: " + ips.size() + ", Failures: " + failedAttempts + ")");
            }
        }
    }
    
    private void analyzeAttackPatterns(List<Map<String, Object>> allLogs, SystemSecurityOverview overview) {
        // Group by IP to identify coordinated attacks
        Map<String, List<Map<String, Object>>> ipLogs = allLogs.stream()
            .filter(log -> log.get("clientIP") != null)
            .collect(Collectors.groupingBy(log -> (String) log.get("clientIP")));
        
        for (Map.Entry<String, List<Map<String, Object>>> entry : ipLogs.entrySet()) {
            String ip = entry.getKey();
            List<Map<String, Object>> logs = entry.getValue();
            
            Set<String> targetUsers = logs.stream()
                .map(log -> (String) log.get("username"))
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());
            
            long failedAttempts = logs.stream()
                .filter(log -> "LOGIN_FAILED".equals(log.get("eventType")))
                .count();
            
            // Potential distributed attack or reconnaissance
            if (targetUsers.size() > 5 && failedAttempts > 10) {
                overview.attackPatterns.add("IP " + ip + " targeted " + targetUsers.size() + " users with " + failedAttempts + " failed attempts");
            }
        }
    }
    
    // === UTILITY METHODS ===
    
    private void calculateOverallThreatLevel(SecurityAnalysisResult result) {
        int riskScore = result.riskFactors.size();
        
        if (riskScore == 0) {
            result.threatLevel = "LOW";
            result.summary = "No significant security threats detected";
        } else if (riskScore <= 2) {
            result.threatLevel = "MEDIUM";
            result.summary = "Minor security concerns detected - monitoring recommended";
        } else if (riskScore <= 4) {
            result.threatLevel = "HIGH";
            result.summary = "Multiple security threats detected - immediate review recommended";
        } else {
            result.threatLevel = "CRITICAL";
            result.summary = "Critical security threats detected - immediate action required";
        }
    }
    
    private void generateSecurityRecommendations(SecurityAnalysisResult result) {
        if (result.riskFactors.contains("BRUTE_FORCE_PATTERN")) {
            result.recommendations.add("Enable account lockout after repeated failed attempts");
            result.recommendations.add("Implement CAPTCHA after 3 failed attempts");
        }
        
        if (result.riskFactors.contains("MULTIPLE_IPS")) {
            result.recommendations.add("Enable email notifications for logins from new locations");
            result.recommendations.add("Consider implementing device registration");
        }
        
        if (result.riskFactors.contains("SUSPICIOUS_GEOGRAPHY")) {
            result.recommendations.add("Enable geographic restrictions for this account");
            result.recommendations.add("Require additional verification for foreign logins");
        }
        
        if (result.riskFactors.contains("UNUSUAL_HOURS")) {
            result.recommendations.add("Monitor activity during unusual hours");
            result.recommendations.add("Consider time-based access restrictions");
        }
        
        if (result.recommendations.isEmpty()) {
            result.recommendations.add("Continue monitoring account activity");
            result.recommendations.add("Ensure strong password policy is enforced");
        }
    }
    
    private String detectCountryFromIP(String ip) {
        // Simplified country detection - in production, use GeoIP service
        if (ip.startsWith("192.168.") || ip.startsWith("10.") || ip.startsWith("127.")) {
            return "LOCAL";  // Private/local IP
        }
        
        // Mock geographic detection based on IP patterns
        if (ip.startsWith("203.")) return "CN";
        if (ip.startsWith("91.")) return "RU"; 
        if (ip.startsWith("46.")) return "IR";
        
        return "US";  // Default to US for demo
    }
    
    private boolean isSuspiciousIP(String ip) {
        // Check for common suspicious patterns
        if (TOR_EXIT_PATTERN.matcher(ip).matches()) {
            return true;
        }
        
        // Check for known suspicious IP ranges (simplified)
        return ip.startsWith("91.") || ip.startsWith("203.");  // Example suspicious ranges
    }
    
    // === RESULT CLASSES ===
    
    public static class SecurityAnalysisResult {
        public String userId;
        public String username;
        public LocalDateTime analysisTimestamp;
        public int daysAnalyzed;
        
        public String threatLevel = "LOW";
        public String summary = "";
        
        // Statistics
        public int totalLoginAttempts = 0;
        public int successfulLogins = 0;
        public int failedLogins = 0;
        public double loginFailureRate = 0.0;
        public int uniqueIPAddresses = 0;
        public int uniqueUserAgents = 0;
        
        // Threats and risks
        public List<String> threats = new ArrayList<>();
        public List<String> riskFactors = new ArrayList<>();
        public List<String> recommendations = new ArrayList<>();
        public List<String> errors = new ArrayList<>();
    }
    
    public static class SystemSecurityOverview {
        public LocalDateTime analysisTimestamp;
        public int daysAnalyzed;
        
        public int totalEvents = 0;
        public int activeUsers = 0;
        public int totalLogins = 0;
        public int totalFailedAttempts = 0;
        public double systemFailureRate = 0.0;
        
        public List<String> highRiskIPs = new ArrayList<>();
        public List<String> suspiciousIPs = new ArrayList<>();
        public List<String> potentiallyCompromisedAccounts = new ArrayList<>();
        public List<String> attackPatterns = new ArrayList<>();
        public List<String> errors = new ArrayList<>();
    }
}