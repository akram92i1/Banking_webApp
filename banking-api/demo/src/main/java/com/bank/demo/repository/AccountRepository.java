package com.bank.demo.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.bank.demo.model.Account;

@Repository
public interface AccountRepository extends JpaRepository<Account, java.util.UUID> {
    // Custom query to find accounts by their account number
    Optional<Account> findByAccountNumber(String accountNumber);


}
