package com.bank.demo.service;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.model.Cards;
import com.bank.demo.repository.Cardsrepository;


@Service
public class Cardservice {
    @Autowired
    private Cardsrepository cardsrepository;

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


}
