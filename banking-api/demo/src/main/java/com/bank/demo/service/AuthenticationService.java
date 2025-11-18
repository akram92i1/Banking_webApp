package com.bank.demo.service;

import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.bank.demo.Dtos.LoginUserDto;
import com.bank.demo.model.Cards;
import com.bank.demo.model.User;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.Cardsrepository;
import com.bank.demo.repository.Userepository;


@Service
public class AuthenticationService {
    @Autowired
    private Userepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private  AuthenticationManager authenticationManager;
    
    @Autowired
    private  Cardsrepository cardsRepository;

    @Autowired
    private  AccountRepository accountRepository;

    public User authenticate(LoginUserDto input) {
        System.out.println("--> Authenticating user with identifier: " + input.getIdentifier());
        authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(input.getIdentifier(), input.getPassword()));
        if  (input.getIdentifier().matches("\\d+")) { 
            System.out.println("Identifier is numeric, treating as card ID.");
            Cards card = cardsRepository.findByCardNumber(input.getIdentifier())
                .orElseThrow(() -> new RuntimeException("Card not found with ID: " + input.getIdentifier()));
            // Get Account associated with the card
            UUID accountId = card.getAccount().getId();
            // Account account = accountRepository.findById(accountId)
            // .orElseThrow(() -> new RuntimeException("Account not found with ID: " + accountId));
             // Get User from Account
            User user = card.getAccount().getUser();
            // Check if identifier is numeric (card ID)
            if (user == null) {
                throw new RuntimeException("User not found for account ID: " + accountId);
            }

            if (!passwordEncoder.matches(input.getPassword(), user.getPasswordHash())) {
            throw new BadCredentialsException("Invalid password");
        }
        else{
            System.out.println("User authenticated successfully with card ID: " + input.getIdentifier());
        }
            return user;
        } else { // Otherwise, treat it as an email
                return    userRepository.findByEmail(input.getIdentifier())
                .orElseThrow(() -> new RuntimeException("User not found with identifier: " + input.getIdentifier()));
        }
    }

}
