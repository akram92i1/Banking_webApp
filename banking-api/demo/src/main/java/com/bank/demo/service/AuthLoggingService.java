package com.bank.demo.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.dto.AuthLogDto;
import com.bank.demo.utils.AsyncAuthLogWriter;

import jakarta.servlet.http.HttpServletRequest;

@Service
public class AuthLoggingService {
    
    @Autowired
    private AsyncAuthLogWriter asyncAuthLogWriter;
    
    // Helper method to extract common request information
    private RequestInfo extractRequestInfo(HttpServletRequest request) {
        String clientIP = getClientIpAddress(request);
        String userAgent = request.getHeader("User-Agent");
        String requestMethod = request.getMethod();
        String path = request.getServletPath();
        
        return new RequestInfo(clientIP, userAgent, requestMethod, path);
    }
    
    // Login event logging methods
    public void logLoginSuccess(String username, String userId, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.loginSuccess(username, userId, info.clientIP, info.userAgent);
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    public void logLoginFailed(String identifier, String reason, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.loginFailed(identifier, info.clientIP, info.userAgent, reason);
        asyncAuthLogWriter.writeLogSync(log.toMap()); // Sync for security events
    }
    
    // Logout event logging methods
    public void logLogoutSuccess(String username, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.logoutSuccess(username, info.clientIP, info.userAgent);
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    public void logLogoutFailed(String reason, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.logoutFailed(reason, info.clientIP, info.userAgent);
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    // JWT Authentication event logging methods
    public void logAuthenticationSuccess(String username, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.authenticationSuccess(username, info.clientIP, info.userAgent, 
            info.requestMethod, info.path);
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    public void logInvalidToken(String username, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.invalidToken(username, info.clientIP, info.userAgent, 
            info.requestMethod, info.path);
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    public void logMissingToken(HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.missingToken(info.clientIP, info.userAgent, 
            info.requestMethod, info.path);
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    public void logBlacklistedToken(HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.blacklistedToken(info.clientIP, info.userAgent, 
            info.requestMethod, info.path);
        asyncAuthLogWriter.writeLogSync(log.toMap()); // Sync for critical security events
    }
    
    public void logAuthenticationError(String errorMessage, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.authenticationError(info.clientIP, info.userAgent, 
            info.requestMethod, info.path, errorMessage);
        asyncAuthLogWriter.writeLogSync(log.toMap()); // Sync for critical errors
    }
    
    // Generic logging method for custom events
    public void logCustomEvent(String event, String username, boolean success, String details, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.custom(event)
            .setUsername(username)
            .setClientIP(info.clientIP)
            .setUserAgent(info.userAgent)
            .setRequestMethod(info.requestMethod)
            .setPath(info.path)
            .setSuccess(success)
            .setDetails(details);
        
        if (success) {
            asyncAuthLogWriter.writeLogAsync(log.toMap());
        } else {
            asyncAuthLogWriter.writeLogSync(log.toMap()); // Sync for failures
        }
    }
    
    // Specific logout event variations
    public void logLogoutInvalidToken(HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.custom("LOGOUT_INVALID_TOKEN")
            .setUsername("unknown")
            .setClientIP(info.clientIP)
            .setUserAgent(info.userAgent)
            .setRequestMethod(info.requestMethod)
            .setPath(info.path)
            .setSuccess(false)
            .setDetails("Logout attempted with invalid token");
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    public void logLogoutError(String errorMessage, HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.custom("LOGOUT_ERROR")
            .setUsername("unknown")
            .setClientIP(info.clientIP)
            .setUserAgent(info.userAgent)
            .setRequestMethod(info.requestMethod)
            .setPath(info.path)
            .setSuccess(false)
            .setDetails("Logout failed with error: " + errorMessage);
        asyncAuthLogWriter.writeLogSync(log.toMap()); // Sync for errors
    }
    
    public void logLogoutNoToken(HttpServletRequest request) {
        RequestInfo info = extractRequestInfo(request);
        AuthLogDto log = AuthLogDto.custom("LOGOUT_NO_TOKEN")
            .setUsername("unknown")
            .setClientIP(info.clientIP)
            .setUserAgent(info.userAgent)
            .setRequestMethod(info.requestMethod)
            .setPath(info.path)
            .setSuccess(false)
            .setDetails("Logout attempted without Authorization header");
        asyncAuthLogWriter.writeLogAsync(log.toMap());
    }
    
    // Helper method to get client IP address
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedForHeader = request.getHeader("X-Forwarded-For");
        if (xForwardedForHeader == null || xForwardedForHeader.isEmpty()) {
            return request.getRemoteAddr();
        } else {
            return xForwardedForHeader.split(",")[0];
        }
    }
    
    // Inner class to hold request information
    private static class RequestInfo {
        final String clientIP;
        final String userAgent;
        final String requestMethod;
        final String path;
        
        RequestInfo(String clientIP, String userAgent, String requestMethod, String path) {
            this.clientIP = clientIP;
            this.userAgent = userAgent;
            this.requestMethod = requestMethod;
            this.path = path;
        }
    }
}