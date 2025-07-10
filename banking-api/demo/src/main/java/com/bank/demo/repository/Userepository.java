package com.bank.demo.repository;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import com.bank.demo.model.User;

// Spring Data JPA creates CRUD implementation at runtime automatically.
public interface Userepository extends JpaRepository<User, UUID> {

    // Custom query to find users by their date of birth
    @Query("SELECT u FROM User u WHERE u.dateOfBirth = :dateOfBirth")
    List<User> findByDateOfBirth(LocalDate dateOfBirth);

    // Custom query to find users by their email
    @Query("SELECT u FROM User u WHERE u.email = :email")
    Optional <User> findByEmail(String email);
}

