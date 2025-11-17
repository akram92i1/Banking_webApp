package com.bank.demo.dto;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

public class AuthLogDto {
    private String timestamp;
    private String event;
    private String username;
    private String userId;
    private String clientIP;
    private String userAgent;
    private String requestMethod;
    private String path;
    private boolean success;
    private String details;
    
    // Private constructor for builder pattern
    private AuthLogDto() {
        this.timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
    }
    
    // Static factory methods for common scenarios
    public static AuthLogDto loginSuccess(String username, String userId, String clientIP, String userAgent) {
        return new AuthLogDto()
            .setEvent("LOGIN_SUCCESS")
            .setUsername(username)
            .setUserId(userId)
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod("POST")
            .setPath("/api/auth/login")
            .setSuccess(true)
            .setDetails("User successfully logged in and JWT token generated");
    }
    
    public static AuthLogDto loginFailed(String identifier, String clientIP, String userAgent, String reason) {
        return new AuthLogDto()
            .setEvent("LOGIN_FAILED")
            .setUsername(identifier)
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod("POST")
            .setPath("/api/auth/login")
            .setSuccess(false)
            .setDetails("Authentication failed: " + reason);
    }
    
    public static AuthLogDto logoutSuccess(String username, String clientIP, String userAgent) {
        return new AuthLogDto()
            .setEvent("LOGOUT_SUCCESS")
            .setUsername(username)
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod("POST")
            .setPath("/api/auth/logout")
            .setSuccess(true)
            .setDetails("User successfully logged out and token blacklisted");
    }
    
    public static AuthLogDto logoutFailed(String reason, String clientIP, String userAgent) {
        return new AuthLogDto()
            .setEvent("LOGOUT_FAILED")
            .setUsername("unknown")
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod("POST")
            .setPath("/api/auth/logout")
            .setSuccess(false)
            .setDetails("Logout failed: " + reason);
    }
    
    public static AuthLogDto authenticationSuccess(String username, String clientIP, String userAgent, String method, String path) {
        return new AuthLogDto()
            .setEvent("AUTHENTICATION_SUCCESS")
            .setUsername(username)
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod(method)
            .setPath(path)
            .setSuccess(true)
            .setDetails("User successfully authenticated");
    }
    
    public static AuthLogDto invalidToken(String username, String clientIP, String userAgent, String method, String path) {
        return new AuthLogDto()
            .setEvent("INVALID_TOKEN")
            .setUsername(username != null ? username : "unknown")
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod(method)
            .setPath(path)
            .setSuccess(false)
            .setDetails("Token validation failed");
    }
    
    public static AuthLogDto missingToken(String clientIP, String userAgent, String method, String path) {
        return new AuthLogDto()
            .setEvent("MISSING_TOKEN")
            .setUsername("unknown")
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod(method)
            .setPath(path)
            .setSuccess(false)
            .setDetails("No Authorization header or invalid format");
    }
    
    public static AuthLogDto blacklistedToken(String clientIP, String userAgent, String method, String path) {
        return new AuthLogDto()
            .setEvent("BLACKLISTED_TOKEN")
            .setUsername("unknown")
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod(method)
            .setPath(path)
            .setSuccess(false)
            .setDetails("Attempt to use blacklisted token - SECURITY VIOLATION");
    }
    
    public static AuthLogDto authenticationError(String clientIP, String userAgent, String method, String path, String errorMessage) {
        return new AuthLogDto()
            .setEvent("AUTHENTICATION_ERROR")
            .setUsername("unknown")
            .setClientIP(clientIP)
            .setUserAgent(userAgent)
            .setRequestMethod(method)
            .setPath(path)
            .setSuccess(false)
            .setDetails("Exception during authentication: " + errorMessage);
    }
    
    // Generic builder method for custom scenarios
    public static AuthLogDto custom(String event) {
        return new AuthLogDto().setEvent(event);
    }
    
    // Fluent setters for builder pattern
    public AuthLogDto setEvent(String event) {
        this.event = event;
        return this;
    }
    
    public AuthLogDto setUsername(String username) {
        this.username = username;
        return this;
    }
    
    public AuthLogDto setUserId(String userId) {
        this.userId = userId;
        return this;
    }
    
    public AuthLogDto setClientIP(String clientIP) {
        this.clientIP = clientIP;
        return this;
    }
    
    public AuthLogDto setUserAgent(String userAgent) {
        this.userAgent = userAgent;
        return this;
    }
    
    public AuthLogDto setRequestMethod(String requestMethod) {
        this.requestMethod = requestMethod;
        return this;
    }
    
    public AuthLogDto setPath(String path) {
        this.path = path;
        return this;
    }
    
    public AuthLogDto setSuccess(boolean success) {
        this.success = success;
        return this;
    }
    
    public AuthLogDto setDetails(String details) {
        this.details = details;
        return this;
    }
    
    // Convert to Map for existing logging infrastructure
    public Map<String, Object> toMap() {
        Map<String, Object> logMap = new HashMap<>();
        logMap.put("timestamp", timestamp);
        logMap.put("event", event);
        logMap.put("username", username);
        if (userId != null) {
            logMap.put("userId", userId);
        }
        logMap.put("clientIP", clientIP);
        logMap.put("userAgent", userAgent);
        logMap.put("requestMethod", requestMethod);
        logMap.put("path", path);
        logMap.put("success", success);
        logMap.put("details", details);
        return logMap;
    }
    
    // Getters
    public String getTimestamp() { return timestamp; }
    public String getEvent() { return event; }
    public String getUsername() { return username; }
    public String getUserId() { return userId; }
    public String getClientIP() { return clientIP; }
    public String getUserAgent() { return userAgent; }
    public String getRequestMethod() { return requestMethod; }
    public String getPath() { return path; }
    public boolean isSuccess() { return success; }
    public String getDetails() { return details; }
    
    @Override
    public String toString() {
        return String.format("AuthLog[%s|%s|%s|%s|%s]", 
            timestamp, event, username, clientIP, success ? "SUCCESS" : "FAILED");
    }
}