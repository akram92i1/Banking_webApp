package com.bank.demo.repository;

import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.bank.demo.model.Account;

@Repository
public interface AccountRepository extends JpaRepository<Account, java.util.UUID> {
    // Custom query to find accounts by their account number
    Optional<Account> findByAccountNumber(@Param("account_number") String accountNumber);
    //find userId with accountId
    @Query("SELECT a.user.id FROM Account a WHERE a.id = :account_id")
    Optional<UUID> findUserIdById(@Param("account_id") UUID id);

}
