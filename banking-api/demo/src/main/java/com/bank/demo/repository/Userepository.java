package com.bank.demo.repository;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import com.bank.demo.model.User;

// Spring Data JPA creates CRUD implementation at runtime automatically.
@Repository
public interface Userepository extends JpaRepository<User, UUID> {

    // Custom query to find users by their date of birth
    @Query("SELECT u FROM User u WHERE u.dateOfBirth = :dateOfBirth")
    List<User> findByDateOfBirth(LocalDate dateOfBirth);

    // Custom query to find users by their email
    @Query("SELECT u FROM User u WHERE u.email = :email")
    Optional <User> findByEmail(String email);
    // Custom query to find users by their card identification number
    @Query("SELECT u FROM User u WHERE u.id = :cardId")
    Optional<User> findByCardIdentificationNumber(String cardId);
    @Transactional
    @Modifying
    @Query("UPDATE User u SET u.passwordHash = :password WHERE u.id = :userId")
    void updatePassword(@Param("userId") UUID userId, @Param("password") String password);

}   

