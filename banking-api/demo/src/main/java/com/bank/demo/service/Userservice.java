package com.bank.demo.service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.model.User;
import com.bank.demo.repository.Userepository;

@Service
public class Userservice {

    @Autowired
    private Userepository userepository;

    public List<User> getAllUsers() {
        return userepository.findAll();
    }

    public Optional<User> getUserById(UUID id) {
        return userepository.findById(id);
    }

    public User createUser(User user) {
        return userepository.save(user);
    }

    public Optional<User> updateUser(UUID id, User userDetails) {
        return userepository.findById(id).map(user -> {
            user.setUsername(userDetails.getUsername());
            user.setEmail(userDetails.getEmail());
            user.setFirstName(userDetails.getFirstName());
            user.setLastName(userDetails.getLastName());
            user.setPhone(userDetails.getPhone());
            user.setDateOfBirth(userDetails.getDateOfBirth());
            user.setRole(userDetails.getRole());
            user.setIsActive(userDetails.getIsActive());
            user.setEmailVerified(userDetails.getEmailVerified());
            user.setFailedLoginAttempts(userDetails.getFailedLoginAttempts());
            user.setLastLoginAt(userDetails.getLastLoginAt());
            user.setUpdatedAt(userDetails.getUpdatedAt());
            // Add other fields as needed
            return userepository.save(user);
        });
    }

    public boolean deleteUser(UUID id) {
        if (userepository.existsById(id)) {
            userepository.deleteById(id);
            return true;
        }
        return false;
    }

    public Optional<User> getUserByEmail(String email) {
        return userepository.findByEmail(email);
    }

    public List<User> getUsersByDateOfBirth(LocalDate dob) {
        return userepository.findByDateOfBirth(dob);
    }
}