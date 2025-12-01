package com.bank.demo.controller;

import java.math.BigDecimal;
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
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.config.JwtUtils;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.enums.TransactionStatus;
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

    @PostMapping("/transfer")
    public ResponseEntity<Transaction> transfer(
            @RequestParam UUID fromAccountId,
            @RequestParam UUID toAccountId,
            @RequestParam BigDecimal amount,
            @RequestParam(required = false) String description) {
        try {
            Transaction transaction = transactionService.transfer(fromAccountId, toAccountId, amount, description);
            return ResponseEntity.ok(transaction);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PostMapping("/transfer-email")
    public ResponseEntity<Transaction> transferByEmail(
            @RequestParam String recipientEmail,
            @RequestParam BigDecimal amount,
            @RequestParam(required = false) String description,
            @RequestParam(defaultValue = "TRANSFER") String transactionType,
            @RequestHeader("Authorization") String authHeader) {
        try {
            // Get authenticated user's email
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            }

            String senderEmail = authentication.getName();
            System.out.println("DEBUG: Transfer by email - Sender: " + senderEmail + ", Recipient: " + recipientEmail
                    + ", Amount: " + amount);

            Transaction transaction = transactionService.transferByEmail(senderEmail, recipientEmail, amount,
                    description);
            return ResponseEntity.ok(transaction);
        } catch (RuntimeException e) {
            System.err.println("ERROR: " + e.getMessage());
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            System.err.println("UNEXPECTED ERROR: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/deposit")
    public ResponseEntity<Transaction> deposit(
            @RequestParam UUID accountId,
            @RequestParam BigDecimal amount,
            @RequestParam(required = false) String description) {
        try {
            Transaction transaction = transactionService.deposit(accountId, amount, description);
            return ResponseEntity.ok(transaction);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping("/{transactionId}/status")
    public ResponseEntity<Transaction> updateTransactionStatus(
            @PathVariable UUID transactionId,
            @RequestParam String status,
            @RequestHeader("Authorization") String authHeader) {
        try {
            // Get authenticated user's email
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            }
            String email = authentication.getName();

            TransactionStatus transactionStatus;
            try {
                transactionStatus = TransactionStatus.valueOf(status.toUpperCase());
            } catch (IllegalArgumentException e) {
                return ResponseEntity.badRequest().build();
            }

            Transaction transaction = transactionService.updateTransactionStatus(transactionId, transactionStatus,
                    email);
            return ResponseEntity.ok(transaction);
        } catch (RuntimeException e) {
            System.err.println("ERROR: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build(); // Assuming runtime exceptions are auth/logic
                                                                        // errors
        } catch (Exception e) {
            System.err.println("UNEXPECTED ERROR: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}