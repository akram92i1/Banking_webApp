package com.bank.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

import com.bank.demo.model.CustomUserDetails;
import com.bank.demo.repository.Userepository;

@Configuration
public class ApplicationConfiguration {
    private final Userepository userRepository;

    public ApplicationConfiguration(Userepository userRepository) {
        this.userRepository = userRepository;
    }

    @Bean
UserDetailsService userDetailsService(Userepository userRepository) {
    System.out.println("--> Initializing UserDetailsService bean.");
    return email -> userRepository.findByEmail(email)
        .map(CustomUserDetails::new)  // wrap User inside CustomUserDetails
        .orElseThrow(() -> new UsernameNotFoundException("User not found"));
}

    @Bean
    BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

   @Bean
    AuthenticationProvider authenticationProvider(UserDetailsService userDetailsService, PasswordEncoder passwordEncoder) {
        DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider(userDetailsService);
        authProvider.setPasswordEncoder(passwordEncoder);
        //DAO stand for Data Access Object
        System.out.println("--> DaoAuthenticationProvider bean initialized.");
        return authProvider;
    }

}
