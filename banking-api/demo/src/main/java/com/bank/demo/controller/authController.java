package com.bank.demo.controller;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.Dtos.LoginUserDto;
import com.bank.demo.config.JwtUtils;
import com.bank.demo.model.User;
import com.bank.demo.responses.LoginResponse;
import com.bank.demo.service.AuthenticationService;
import com.bank.demo.service.TokenBlacklistService;
import com.bank.demo.utils.AuthLogWriter;

import jakarta.servlet.http.HttpServletRequest;

@RestController
@RequestMapping("/api/auth")
public class authController {
   @Autowired
    private AuthenticationService authenticationService;

    @Autowired
    private JwtUtils jwtUtils;

    @Autowired
    TokenBlacklistService tokenBlacklistService;
    
    @Autowired
    private AuthLogWriter authLogWriter;

    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@RequestBody LoginUserDto LoginUserDto, HttpServletRequest request) {
        String clientIP = getClientIpAddress(request);
        String userAgent = request.getHeader("User-Agent");
        String requestMethod = request.getMethod();
        String path = request.getServletPath();
        
        System.out.println("Received login request for identifier: " + LoginUserDto.getIdentifier());
        
        try {
            User authenticatedUser = authenticationService.authenticate(LoginUserDto);
            
            String jwtToken = jwtUtils.generateToken(authenticatedUser.getId(), authenticatedUser.getEmail());
            System.out.println("Generated JWT Token: " + jwtToken);
            boolean tokenValid = jwtUtils.validateToken(jwtToken);
            // TODO: Handle the logging system asynchronously to avoid blocking the main thread
            // TODO : Implement log through DTO to standardize log format and make a lighter log writer in the controllers 
            // Log successful login
            
            Map<String, Object> logData = new HashMap<>();
            logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            logData.put("event", "LOGIN_SUCCESS");
            logData.put("username", authenticatedUser.getEmail());
            logData.put("userId", authenticatedUser.getId().toString());
            logData.put("clientIP", clientIP);
            logData.put("userAgent", userAgent);
            logData.put("requestMethod", requestMethod);
            logData.put("path", path);
            logData.put("success", true);
            logData.put("details", "User successfully logged in and JWT token generated");
            authLogWriter.writeLog(logData);
            
            LoginResponse loginResponse = new LoginResponse(jwtToken, Boolean.toString(tokenValid));
            loginResponse.setExpirationTime(jwtUtils.getExpirationTime(jwtToken));
            return ResponseEntity.ok(loginResponse);
            
        } catch (Exception e) {
            // Log failed login attempt
            Map<String, Object> logData = new HashMap<>();
            logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            logData.put("event", "LOGIN_FAILED");
            logData.put("username", LoginUserDto.getIdentifier()); // Could be email or card ID
            logData.put("clientIP", clientIP);
            logData.put("userAgent", userAgent);
            logData.put("requestMethod", requestMethod);
            logData.put("path", path);
            logData.put("success", false);
            logData.put("details", "Authentication failed: " + e.getMessage());
            authLogWriter.writeLog(logData);
            
            System.out.println("Authentication failed for identifier: " + LoginUserDto.getIdentifier());
            return ResponseEntity.badRequest().body("Authentication failed: " + e.getMessage());
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<String> logoutUser(HttpServletRequest request) {
        String clientIP = getClientIpAddress(request);
        String userAgent = request.getHeader("User-Agent");
        String requestMethod = request.getMethod();
        String path = request.getServletPath();
        String authHeader = request.getHeader("Authorization");
        
        System.out.println("Processing logout request...");
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            System.out.println("Extracted token for logout: " + token.substring(0, 20) + "...");
            
            try {
                if (jwtUtils.validateToken(token)) {
                    // Get user email from token before blacklisting
                    String userEmail = jwtUtils.getEmailFromToken(token);
                    
                    long expiry = jwtUtils.getExpirationTime(token);
                    Instant expiryInstant = Instant.ofEpochMilli(expiry);
                    tokenBlacklistService.blacklistToken(token, expiryInstant);
                    
                    // Log successful logout
                    Map<String, Object> logData = new HashMap<>();
                    logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                    logData.put("event", "LOGOUT_SUCCESS");
                    logData.put("username", userEmail);
                    logData.put("clientIP", clientIP);
                    logData.put("userAgent", userAgent);
                    logData.put("requestMethod", requestMethod);
                    logData.put("path", path);
                    logData.put("success", true);
                    logData.put("details", "User successfully logged out and token blacklisted");
                    authLogWriter.writeLog(logData);
                    
                    return ResponseEntity.ok("User logged out successfully.");
                } else {
                    // Log logout attempt with invalid token
                    Map<String, Object> logData = new HashMap<>();
                    logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                    logData.put("event", "LOGOUT_INVALID_TOKEN");
                    logData.put("username", "unknown");
                    logData.put("clientIP", clientIP);
                    logData.put("userAgent", userAgent);
                    logData.put("requestMethod", requestMethod);
                    logData.put("path", path);
                    logData.put("success", false);
                    logData.put("details", "Logout attempted with invalid token");
                    authLogWriter.writeLog(logData);
                    
                    return ResponseEntity.badRequest().body("Invalid token for logout.");
                }
            } catch (Exception e) {
                // Log logout error
                Map<String, Object> logData = new HashMap<>();
                logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                logData.put("event", "LOGOUT_ERROR");
                logData.put("username", "unknown");
                logData.put("clientIP", clientIP);
                logData.put("userAgent", userAgent);
                logData.put("requestMethod", requestMethod);
                logData.put("path", path);
                logData.put("success", false);
                logData.put("details", "Logout failed with error: " + e.getMessage());
                authLogWriter.writeLog(logData);
                
                return ResponseEntity.status(500).body("Logout failed: " + e.getMessage());
            }
        } else {
            // Log logout attempt without proper authorization header
            Map<String, Object> logData = new HashMap<>();
            logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            logData.put("event", "LOGOUT_NO_TOKEN");
            logData.put("username", "unknown");
            logData.put("clientIP", clientIP);
            logData.put("userAgent", userAgent);
            logData.put("requestMethod", requestMethod);
            logData.put("path", path);
            logData.put("success", false);
            logData.put("details", "Logout attempted without Authorization header");
            authLogWriter.writeLog(logData);
            
            return ResponseEntity.badRequest().body("Invalid Authorization header.");
        }
    }

    @GetMapping("/test")
    public ResponseEntity<String> testEndpoint() {
        return ResponseEntity.ok("Authentication service is up and running!");
    }

    @GetMapping("/authenticationStatus")
    public ResponseEntity<String> getAuthenticationStatus(@RequestBody String token) {
        long jwtTokenExprirationTime = jwtUtils.getExpirationTime(token);
        return ResponseEntity.ok("Token is valid expriration time: " + jwtTokenExprirationTime);
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

    // Request DTOs
    public static class LoginRequest {
        private String identifier; // This can be email or card ID
        private String email;   // For email login
        private String password; // Password for authentication
        
        // Getters and setters
        public String getIdentifier() { return identifier; }
        public void setIdentifier(String identifier) { this.identifier = identifier; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getPassword() { return password; }
        public void setPassword(String password) { this.password = password; }
    }
}