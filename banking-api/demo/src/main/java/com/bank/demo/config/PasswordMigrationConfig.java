package com.bank.demo.config;

import com.bank.demo.model.User;
import com.bank.demo.repository.Userepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;

@Configuration
public class PasswordMigrationConfig {

    @Bean
    public CommandLineRunner migratePasswords(Userepository userRepository, PasswordEncoder passwordEncoder) {
        return args -> {
            System.out.println("--> Checking for users with plaintext passwords...");
            List<User> users = userRepository.findAll();
            int updatedCount = 0;

            for (User user : users) {
                String currentPassword = user.getPasswordHash();
                // Check if password is not null and does not start with the BCrypt prefix
                if (currentPassword != null && !currentPassword.startsWith("$2a$")) {
                    String hashedPassword = passwordEncoder.encode(currentPassword);
                    userRepository.updatePassword(user.getId(), hashedPassword);
                    updatedCount++;
                }
            }

            if (updatedCount > 0) {
                System.out.println("--> Migrated " + updatedCount + " users to BCrypt password hashing.");
            } else {
                System.out.println("--> No users with plaintext passwords found.");
            }
        };
    }
}
