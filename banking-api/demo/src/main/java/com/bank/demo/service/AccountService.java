package com.bank.demo.service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.model.Account;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.Userepository;


@Service
public class AccountService {
    @Autowired
    private AccountRepository accountRepository;
    @Autowired
    private Userepository userRepository;
    
    public String getEmailByAccountId(UUID accountId) {
        System.out.println("Fetching email for accountId: " + accountId);
        Optional<UUID> userId = accountRepository.findUserIdById(accountId);
        System.out.println("User ID from accountId: -----> " + userId);
        if (userId.isPresent()) {
            Optional<String> email = userRepository.findEmailByUserId(userId.get());
            return email.orElse(null);
        }
        return null;
    }

    public List<Account> getAccountsByUserId(UUID userId) {
        return accountRepository.findByUserId(userId);
    }

    public Account getAccountById(UUID accountId) {
        return accountRepository.findById(accountId).orElse(null);
    }
}
