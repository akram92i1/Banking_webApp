package com.bank.demo.controller;

// Import necessary Java and Spring libraries
// Import necessary Java libraries
import  java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.model.Cards;
import com.bank.demo.service.Cardservice;

@RestController
@RequestMapping("/api/cards")
public class cardController {
    @Autowired
    private Cardservice cardservice;

    @GetMapping
    public List<Cards> getAllCards() {
        return cardservice.getAllCards();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Cards> getCardById(@PathVariable UUID id) {
        Optional<Cards> card = cardservice.getCardById(id);
        return card.map(ResponseEntity::ok)
                   .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Cards> createCard(@RequestBody Cards card) {
        Cards created = cardservice.createCard(card);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/expiration")
    public List<Cards> getCardByExpirationDate(@RequestParam("date") String date) {
        OffsetDateTime expirationDate = OffsetDateTime.parse(date);
        return cardservice.getCardByExpirationDate(expirationDate);
    }

    @GetMapping("/account/{accountId}")
    public ResponseEntity<List<Cards>> getCardsByAccountId(@PathVariable UUID accountId) {
        List<Cards> cards = cardservice.getCardsByAccountId(accountId);
        return ResponseEntity.ok(cards);
    }
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCard(@PathVariable UUID id) {
        Cards deleted = cardservice.deleteCard(id);
        return deleted != null ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }    
}
