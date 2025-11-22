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
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.config.JwtUtils;
import com.bank.demo.dto.AccountDto;
import com.bank.demo.mapper.AccountMapper;
import com.bank.demo.model.Account;
import com.bank.demo.model.User;
import com.bank.demo.service.AccountService;
import com.bank.demo.service.Userservice;

@RestController
@RequestMapping("/api/accounts")
public class AccountController {
    
    @Autowired
    private AccountService accountService;
    
    @Autowired
    private Userservice userService;
    
    @Autowired
    private JwtUtils jwtUtils;
    
    @Autowired
    private AccountMapper accountMapper;

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<AccountDto>> getUserAccounts(@PathVariable UUID userId, @RequestHeader("Authorization") String authHeader) {
        try {
            // Extract email from JWT token
            String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
            String emailFromToken = jwtUtils.getEmailFromToken(token);
            
            // Get user by ID to verify ownership
            Optional<User> userOpt = userService.getUserById(userId);
            if (userOpt.isEmpty()) {
                return ResponseEntity.notFound().build();
            }
            
            User user = userOpt.get();
            
            // Verify the user from token matches the requested user
            if (!user.getEmail().equals(emailFromToken)) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }
            
            List<Account> accounts = accountService.getAccountsByUserId(userId);
            List<AccountDto> accountDtos = accountMapper.toDtoList(accounts);
            return ResponseEntity.ok(accountDtos);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/current-user")
    public ResponseEntity<List<AccountDto>> getCurrentUserAccounts(@RequestHeader("Authorization") String authHeader) {
        try {
            System.out.println("####### DEBUG: Getting accounts for current user");
            // Get current authenticated user
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String email = authentication.getName();
            
            System.out.println("DEBUG: Getting accounts for user email: " + email);
            
            // Find user by email
            Optional<User> userOpt = userService.getUserByEmail(email);
            if (userOpt.isEmpty()) {
                System.out.println("DEBUG: User not found for email: " + email);
                return ResponseEntity.notFound().build();
            }
            User user = userOpt.get();
            
            System.out.println("DEBUG: Found user with ID: " + user.getId() + ", Name: " + user.getFirstName() + " " + user.getLastName());
            
            List<Account> accounts = accountService.getAccountsByUserId(user.getId());
            System.out.println("DEBUG: Found " + accounts.size() + " accounts");
            
            for (Account account : accounts) {
                System.out.println("DEBUG: Account ID: " + account.getId() + 
                    ", Number: " + account.getAccountNumber() + 
                    ", Balance: " + account.getBalance() + 
                    ", Available: " + account.getAvailableBalance());
            }
            
            // Convert to DTOs to avoid serialization issues
            List<AccountDto> accountDtos = accountMapper.toDtoList(accounts);
            System.out.println("DEBUG: Successfully converted " + accountDtos.size() + " accounts to DTOs");
            
            return ResponseEntity.ok(accountDtos);
        } catch (Exception e) {
            System.out.println("DEBUG: Error in getCurrentUserAccounts: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/{accountId}/balance")
    public ResponseEntity<Object> getAccountBalance(@PathVariable UUID accountId, @RequestHeader("Authorization") String authHeader) {
        try {
            // Extract email from JWT token
            String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
            String emailFromToken = jwtUtils.getEmailFromToken(token);
            
            // Verify account ownership
            String accountOwnerEmail = accountService.getEmailByAccountId(accountId);
            if (!emailFromToken.equals(accountOwnerEmail)) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }
            
            Account account = accountService.getAccountById(accountId);
            if (account == null) {
                return ResponseEntity.notFound().build();
            }
            
            return ResponseEntity.ok(new BalanceResponse(account.getBalance(), account.getAvailableBalance()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // Inner class for balance response
    public static class BalanceResponse {
        private java.math.BigDecimal balance;
        private java.math.BigDecimal availableBalance;

        public BalanceResponse(java.math.BigDecimal balance, java.math.BigDecimal availableBalance) {
            this.balance = balance;
            this.availableBalance = availableBalance;
        }

        public java.math.BigDecimal getBalance() {
            return balance;
        }

        public void setBalance(java.math.BigDecimal balance) {
            this.balance = balance;
        }

        public java.math.BigDecimal getAvailableBalance() {
            return availableBalance;
        }

        public void setAvailableBalance(java.math.BigDecimal availableBalance) {
            this.availableBalance = availableBalance;
        }
    }
}