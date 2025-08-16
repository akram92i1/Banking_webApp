package com.bank.demo.config;

import java.util.List;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import com.bank.demo.model.User;
import com.bank.demo.repository.Userepository;

import jakarta.annotation.PostConstruct;

@Component
public class PasswordMigrationService {

    private final Userepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public PasswordMigrationService(Userepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    
    @PostConstruct
    public void migratePasswords() {
    List<User> users = userRepository.findAll();

    for (User user : users) {
        String password = user.getPasswordHash();
        if (password.startsWith("$2a$") || password.startsWith("$2b$")) {
            System.out.println("--> Already encoded: " + user.getEmail());
            continue;
        }

        String encodedPassword = passwordEncoder.encode(password);
        userRepository.updatePassword(user.getId(), encodedPassword);
        System.out.println("--> Migrated password for user: " + user.getEmail());
    }
}


}
