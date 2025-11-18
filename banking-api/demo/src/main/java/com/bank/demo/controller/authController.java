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
import com.bank.demo.service.AuthLoggingService;
import com.bank.demo.service.AuthenticationService;
import com.bank.demo.service.TokenBlacklistService;
import com.bank.demo.utils.AsyncAuthLogWriter;

import jakarta.servlet.http.HttpServletRequest;

@RestController
@RequestMapping("/api/auth")
public class authController {
   @Autowired
    private AuthenticationService authenticationService;

    @Autowired
    private JwtUtils jwtUtils;

    @Autowired
    private TokenBlacklistService tokenBlacklistService;
    
    @Autowired
    private AuthLoggingService authLoggingService;
    
    @Autowired
    private AsyncAuthLogWriter asyncAuthLogWriter;

    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@RequestBody LoginUserDto loginUserDto, HttpServletRequest request) {
        System.out.println("Received login request for identifier: " + loginUserDto.getIdentifier());
        
        try {
            User authenticatedUser = authenticationService.authenticate(loginUserDto);
            
            String jwtToken = jwtUtils.generateToken(authenticatedUser.getId(), authenticatedUser.getEmail());
            System.out.println("Generated JWT Token: " + jwtToken);
            boolean tokenValid = jwtUtils.validateToken(jwtToken);
            
            // Log successful login - clean and simple
            authLoggingService.logLoginSuccess(
                authenticatedUser.getEmail(), 
                authenticatedUser.getId().toString(), 
                request
            );
            
            LoginResponse loginResponse = new LoginResponse(jwtToken, Boolean.toString(tokenValid));
            loginResponse.setExpirationTime(jwtUtils.getExpirationTime(jwtToken));
            return ResponseEntity.ok(loginResponse);
            
        } catch (Exception e) {
            // Log failed login attempt - clean and simple
            authLoggingService.logLoginFailed(
                loginUserDto.getIdentifier(), 
                e.getMessage(), 
                request
            );
            
            System.out.println("Authentication failed for identifier: " + loginUserDto.getIdentifier());
            return ResponseEntity.badRequest().body("Authentication failed: " + e.getMessage());
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<String> logoutUser(HttpServletRequest request) {
        System.out.println("Processing logout request...");
        
        String authHeader = request.getHeader("Authorization");
        
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
                    
                    // Log successful logout - clean and simple
                    authLoggingService.logLogoutSuccess(userEmail, request);
                    
                    return ResponseEntity.ok("User logged out successfully.");
                } else {
                    // Log logout attempt with invalid token - clean and simple
                    authLoggingService.logLogoutInvalidToken(request);
                    
                    return ResponseEntity.badRequest().body("Invalid token for logout.");
                }
            } catch (Exception e) {
                // Log logout error - clean and simple
                authLoggingService.logLogoutError(e.getMessage(), request);
                
                return ResponseEntity.status(500).body("Logout failed: " + e.getMessage());
            }
        } else {
            // Log logout attempt without proper authorization header - clean and simple
            authLoggingService.logLogoutNoToken(request);
            
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
    
    @GetMapping("/logging-status")
    public ResponseEntity<Map<String, Object>> getLoggingStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("asyncLoggerActive", true);
        status.put("pendingLogs", asyncAuthLogWriter.getBufferSize());
        status.put("loggingMode", "standardized-async");
        status.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        return ResponseEntity.ok(status);
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