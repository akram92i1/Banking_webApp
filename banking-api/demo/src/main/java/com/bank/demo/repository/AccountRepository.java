package com.bank.demo.repository;

import java.util.List;
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

    //find first accountId with userId 
    @Query("SELECT a.id FROM Account a WHERE a.user.id = :user_id")
    Optional<UUID> findFirstAccountIdByUserId(@Param("user_id") UUID userId);

    //find all accounts by userId with EAGER fetch for user to avoid lazy loading issues
    @Query("SELECT a FROM Account a JOIN FETCH a.user WHERE a.user.id = :user_id")
    List<Account> findByUserId(@Param("user_id") UUID userId);

    // Native query as backup to test if JPA mapping is the issue
    @Query(value = "SELECT account_id, account_number, balance, available_balance, account_type, account_status FROM accounts WHERE user_id = :user_id", nativeQuery = true)
    List<Object[]> findAccountDataByUserIdNative(@Param("user_id") UUID userId);

    // Find accounts by user email for email-based transfers
    @Query("SELECT a FROM Account a JOIN FETCH a.user WHERE a.user.email = :email")
    List<Account> findByUserEmail(@Param("email") String email);

    // Find primary account by user email (first account)
    @Query("SELECT a FROM Account a JOIN FETCH a.user WHERE a.user.email = :email ORDER BY a.createdAt ASC")
    Optional<Account> findPrimaryAccountByUserEmail(@Param("email") String email);
}
