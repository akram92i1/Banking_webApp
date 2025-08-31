package com.bank.demo.repository;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.bank.demo.model.Cards;

@Repository
// Spring Data JPA creates CRUD implementation at runtime automatically.
public interface Cardsrepository extends JpaRepository<Cards, UUID> {
    // Custom query to find cards by their card number
    @Query("SELECT c FROM Cards c WHERE c.cardNumberHash = :cardNumberHash")
    Optional<Cards> findByCardNumber(String cardNumberHash);
    // Custom query to find cards by their account ID
    @Query("SELECT c FROM Cards c WHERE c.account.id = :accountId")
    List<Cards> findByAccountId(@Param("accountId") UUID accountId);
    // find by expriration date
    @Query("SELECT c FROM Cards c WHERE c.expiryDate = :expiryDate")
    List<Cards> findByExpiryDate(OffsetDateTime expiryDate);
    // find accountId with cardId
    @Query("SELECT c.account.id FROM Cards c WHERE c.id = :cardId")
    Optional<UUID> findAccountIdByCardId(@Param("cardId") UUID card);
}     
