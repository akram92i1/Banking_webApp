package com.bank.demo.service;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.model.Cards;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.Cardsrepository;
import com.bank.demo.repository.Userepository;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
@Service
public class Cardservice {
    @Autowired
    private Cardsrepository cardsrepository;
    @Autowired
    private Userepository userepository;
    @Autowired
    private AccountRepository accountRepository;


    public List<Cards> getAllCards() {
        return cardsrepository.findAll();
    }
    public Optional<Cards> getCardById(UUID id) {
        return cardsrepository.findById(id);
    }
    public Cards createCard(Cards card) {
        return cardsrepository.save(card);
    }
    public List<Cards> getCardsByAccountId(UUID accountId) {
        System.err.println("Fetching cards for account ID: " + accountId);
        return cardsrepository.findByAccountId(accountId);
        
    }
    public Optional<UUID> getAccountIdByCardId(UUID cardId) {
        return cardsrepository.findAccountIdByCardId(cardId);
    }

    public List <Cards> getCardByExpirationDate(OffsetDateTime expirationDate) {
        return cardsrepository.findByExpiryDate(expirationDate);
    }
    
    public Cards deleteCard(UUID id) {
        Optional<Cards> card = cardsrepository.findById(id);
        if (card.isPresent()) {
            cardsrepository.delete(card.get());
            return card.get();
        }
        return null; // or throw an exception
    }

    public Cards getCardInformation() {
        // Get the connected user information
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userEmail = authentication.getName(); // this comes from the JWT subject
        // Fetch the userId using the userEmail
        Optional <UUID> userIdOpt = userepository.findByEmail(userEmail).map(user -> user.getId());
        UUID userId = userIdOpt.orElse(null);
        if (userId == null) {
            System.err.println("User not found for email: " + userEmail);
            return null; // or throw an exception
        }
        else {
           //Fetch the accountId using the userId
              Optional <UUID> accountIdOpt = accountRepository.findByUserId(userId);
              UUID accountId = accountIdOpt.orElse(null);
                if (accountId == null) {
                    System.err.println("Account not found for userId: " + userId);
                    return null; // or throw an exception
                }
                else{
                    System.out.println("Account ID for user " + userEmail + ": " + accountId);
                    // Fetch the card information using the accountId
                    List<Cards> cardOpt = cardsrepository.findByAccountId(accountId);
                    if (!cardOpt.isEmpty()) {
                        return cardOpt.get(0);
                    } else {
                        System.err.println("No cards found for accountId: " + accountId);
                        return null; // or throw an exception
                    }
                }

        }
    }
}
