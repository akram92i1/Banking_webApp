package com.bank.demo.controller;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.config.JwtUtils;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.User;
import com.bank.demo.service.TransactionService;
import com.bank.demo.service.Userservice;

@RestController
@RequestMapping("/api/transactions")
public class TransactionController {

    @Autowired
    private TransactionService transactionService;
    
    @Autowired
    private Userservice userService;
    
    @Autowired
    private JwtUtils jwtUtils;

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Transaction>> getUserTransactions(
            @PathVariable UUID userId,
            @RequestParam(defaultValue = "10") int limit,
            @RequestHeader("Authorization") String authHeader) {
        try {
            // Extract email from JWT token
            String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
            String emailFromToken = jwtUtils.getEmailFromToken(token);
            
            // Get user by ID to verify ownership
            User user = userService.getUserById(userId).orElse(null);
            if (user == null) {
                return ResponseEntity.notFound().build();
            }
            
            // Verify the user from token matches the requested user
            if (!user.getEmail().equals(emailFromToken)) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }
            
            List<Transaction> transactions = transactionService.getTransactionsByUserId(userId, limit);
            return ResponseEntity.ok(transactions);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/current-user")
    public ResponseEntity<List<Transaction>> getCurrentUserTransactions(
            @RequestParam(defaultValue = "10") int limit,
            @RequestHeader("Authorization") String authHeader) {
        try {
            // Get current authenticated user
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String email = authentication.getName();
            
            System.out.println("DEBUG: Getting transactions for user: " + email + " with limit: " + limit);
            
            // Find user by email
            Optional<User> userOpt = userService.getUserByEmail(email);
            if (userOpt.isEmpty()) {
                System.out.println("DEBUG: User not found for email: " + email);
                return ResponseEntity.notFound().build();
            }
            User user = userOpt.get();
            
            List<Transaction> transactions = transactionService.getTransactionsByUserId(user.getId(), limit);
            System.out.println("DEBUG: Found " + transactions.size() + " transactions for user " + user.getId());
            
            if (!transactions.isEmpty()) {
                Transaction firstTransaction = transactions.get(0);
                System.out.println("DEBUG: First transaction - ID: " + firstTransaction.getTransactionId() + 
                                 ", Amount: " + firstTransaction.getAmount() + 
                                 ", Type: " + firstTransaction.getTransactionType());
            }
            
            return ResponseEntity.ok(transactions);
        } catch (Exception e) {
            System.err.println("ERROR in getCurrentUserTransactions: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/account/{accountId}")
    public ResponseEntity<List<Transaction>> getAccountTransactions(
            @PathVariable UUID accountId,
            @RequestParam(defaultValue = "10") int limit,
            @RequestHeader("Authorization") String authHeader) {
        try {
            // Extract email from JWT token
            String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
            String emailFromToken = jwtUtils.getEmailFromToken(token);
            
            // Verify account ownership through AccountService
            // This would require updating AccountService.getEmailByAccountId
            // For now, we'll implement basic security
            
            List<Transaction> transactions = transactionService.getTransactionsByAccountId(accountId, limit);
            return ResponseEntity.ok(transactions);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}