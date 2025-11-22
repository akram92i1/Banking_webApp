package com.bank.demo.service;

import java.util.List;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import com.bank.demo.model.Transaction;
import com.bank.demo.repository.transactionRepository;

@Service
public class TransactionService {

    @Autowired
    private transactionRepository transactionRepository;

    public List<Transaction> getTransactionsByUserId(UUID userId, int limit) {
        PageRequest pageRequest = PageRequest.of(0, limit, Sort.by(Sort.Direction.DESC, "createdAt"));
        return transactionRepository.findByUserIdOrderByCreatedAtDesc(userId, pageRequest);
    }

    public List<Transaction> getTransactionsByAccountId(UUID accountId, int limit) {
        PageRequest pageRequest = PageRequest.of(0, limit, Sort.by(Sort.Direction.DESC, "createdAt"));
        return transactionRepository.findByAccountIdOrderByCreatedAtDesc(accountId, pageRequest);
    }
}