package com.bank.demo.controller;

import java.time.Instant;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpRequest;
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

@RestController
@RequestMapping("/api/auth")
public class authController {
   @Autowired
    private AuthenticationService authenticationService;

    @Autowired
    private JwtUtils jwtUtils;

    @Autowired
    TokenBlacklistService tokenBlacklistService;



    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@RequestBody LoginUserDto LoginUserDto) {
        System.out.println("Received login request for identifier: " + LoginUserDto.getIdentifier());
        
        User authenticatedUser = authenticationService.authenticate(LoginUserDto);
        
        String jwtToken = jwtUtils.generateToken(authenticatedUser.getId(),authenticatedUser.getEmail());
        System.out.println("Generated JWT Token: " + jwtToken);
        boolean tokenValid = jwtUtils.validateToken(jwtToken);
        
        LoginResponse loginResponse = new LoginResponse(jwtToken , Boolean.toString(tokenValid));
        loginResponse.setExpirationTime(jwtUtils.getExpirationTime(jwtToken));
        return ResponseEntity.ok(loginResponse);
    }

    @PostMapping("/logout")
    public ResponseEntity<String> logoutUser(HttpRequest request){
        String authHeader = request.getHeaders().getFirst("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            if(jwtUtils.validateToken(token))
            {
                long expiry = jwtUtils.getExpirationTime(token);
                Instant expiryInstant = Instant.ofEpochMilli(expiry);
                tokenBlacklistService.blacklistToken(token, expiryInstant);
            }
            return ResponseEntity.ok("User logged out successfully.");
        } else {
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
