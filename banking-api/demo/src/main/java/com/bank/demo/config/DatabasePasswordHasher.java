package com.bank.demo.config;

import com.bank.demo.model.User;
import com.bank.demo.repository.Userepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Component
@Order(1)
public class DatabasePasswordHasher implements CommandLineRunner {

    private final Userepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DatabasePasswordHasher(Userepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) throws Exception {
        System.out.println("--> Checking for users with plain text passwords...");
        List<User> users = userRepository.findAll();
        int updatedCount = 0;

        Map<String, String> demoCredentials = new LinkedHashMap<>();
        demoCredentials.put("jdoe@example.com", "pass1");
        demoCredentials.put("asmith@example.com", "pass2");

        for (User user : users) {
            String currentPassword = user.getPasswordHash();
            String expectedDemoPassword = demoCredentials.get(user.getEmail());

            if (expectedDemoPassword != null &&
                    (currentPassword == null ||
                            !isBcryptHash(currentPassword) ||
                            !passwordEncoder.matches(expectedDemoPassword, currentPassword))) {
                String hashedPassword = passwordEncoder.encode(expectedDemoPassword);
                userRepository.updatePassword(user.getId(), hashedPassword);
                updatedCount++;
                continue;
            }

            // Check if the password is NOT hashed with BCrypt
            // BCrypt hashes typically start with $2a$, $2b$, or $2y$
            if (currentPassword != null && !isBcryptHash(currentPassword)) {

                String hashedPassword = passwordEncoder.encode(currentPassword);
                userRepository.updatePassword(user.getId(), hashedPassword);
                updatedCount++;
            }
        }

        System.out.println("--> Migrated " + updatedCount + " users to hashed passwords.");
    }

    private boolean isBcryptHash(String value) {
        return value.startsWith("$2a$") || value.startsWith("$2b$") || value.startsWith("$2y$");
    }
}
