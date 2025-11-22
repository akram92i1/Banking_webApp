package com.bank.demo.mapper;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;

import com.bank.demo.dto.AccountDto;
import com.bank.demo.model.Account;

@Service
public class AccountMapper {
    
    public AccountDto toDto(Account account) {
        if (account == null) {
            return null;
        }
        
        AccountDto dto = new AccountDto();
        dto.setId(account.getId());
        dto.setAccountNumber(account.getAccountNumber());
        dto.setAccountType(account.getAccountType());
        dto.setAccountStatus(account.getAccountStatus());
        dto.setBalance(account.getBalance());
        dto.setAvailableBalance(account.getAvailableBalance());
        dto.setCreditLimit(account.getCreditLimit());
        dto.setInterestRate(account.getInterestRate());
        dto.setOverdraftLimit(account.getOverdraftLimit());
        dto.setMinimumBalance(account.getMinimumBalance());
        dto.setOpenedAt(account.getOpenedAt());
        dto.setClosedAt(account.getClosedAt());
        dto.setCreatedAt(account.getCreatedAt());
        dto.setUpdatedAt(account.getUpdatedAt());
        
        // Safely access lazy-loaded properties
        if (account.getUser() != null) {
            dto.setUserId(account.getUser().getId());
            dto.setUserFirstName(account.getUser().getFirstName());
            dto.setUserLastName(account.getUser().getLastName());
        }
        
        if (account.getBank() != null) {
            dto.setBankId(account.getBank().getId());
            dto.setBankName(account.getBank().getBankName());
        }
        
        return dto;
    }
    
    public List<AccountDto> toDtoList(List<Account> accounts) {
        if (accounts == null) {
            return null;
        }
        
        return accounts.stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }
}