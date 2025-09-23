package com.bank.demo.service;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.Dtos.TransferRequestDto;
import com.bank.demo.Dtos.TransferRequestDto.AutoDepositRequest;
import com.bank.demo.Dtos.TransferRequestDto.AutoDepositResponse;
import com.bank.demo.Dtos.TransferRequestDto.TransferRequest;
import com.bank.demo.Dtos.TransferRequestDto.TransferResponse;
import com.bank.demo.Dtos.TransferRequestDto.TransferStatusResponse;
import com.bank.demo.exceptions.InsufficientFundsException;
import com.bank.demo.mapper.TransactionMapper;
import com.bank.demo.model.Account;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.enums.TransactionType;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.transactionRepository;
@Service
public class bankTransactionService {

    // Colors
public static final String ANSI_RESET = "\u001B[0m";
public static final String ANSI_RED = "\u001B[31m";
public static final String ANSI_GREEN = "\u001B[32m";
public static final String ANSI_YELLOW = "\u001B[33m";
public static final String ANSI_BLUE = "\u001B[34m";
public static final String ANSI_PURPLE = "\u001B[35m";
public static final String ANSI_CYAN = "\u001B[36m";


    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private transactionRepository transactionRepository;

    public TransferResponse sendMoney(TransferRequest request) throws InsufficientFundsException {
    System.out.println(ANSI_PURPLE +"--> sendMoney() called in bankTransactionService"+ANSI_RESET);
    System.err.println(ANSI_BLUE+"Here is the request: " + request+ANSI_RESET);
    System.out.println("--> Initiating sendMoney from " + request.getFromAccountId() + " to " + request.getToAccountId() + " amount: " + request.getAmount());

    Account fromAccount = accountRepository.findByAccountNumber(request.getFromAccountId())
        .orElseThrow(() -> new IllegalArgumentException("Account not found"));
    System.out.println(ANSI_GREEN +"--> From Account: " + fromAccount.getAccountNumber() + ", Balance: " + fromAccount.getBalance()+ANSI_RESET);

    BigDecimal requestAmount = BigDecimal.valueOf(request.getAmount());
    System.out.println(ANSI_YELLOW +"--> Requested Amount: " + requestAmount +ANSI_RESET);

    if(fromAccount.getBalance().compareTo(requestAmount)<0){
        throw new InsufficientFundsException("Not enough balance to complete transfer");
    }
    fromAccount.setBalance(fromAccount.getBalance().subtract(requestAmount));
    System.out.println(ANSI_RED +"--> New From Account Balance: " + fromAccount.getBalance()+ANSI_RESET);

    System.out.println(ANSI_CYAN +"--> Transaction Type: " + request.getTransactionType()+ANSI_RESET);
    String typeString = request.getTransactionType();
    TransactionType typeEnum = TransactionType.valueOf(typeString);

    Account toAccount = accountRepository.findByAccountNumber(request.getToAccountId())
        .orElseThrow(()-> new IllegalArgumentException("Recipient Account not found"));
    System.out.println(ANSI_GREEN +"--> To Account: " + toAccount.getAccountNumber() + ", Balance: " + toAccount.getBalance()+ANSI_RESET);

    // Use TransactionMapper to map DTO to entity
    Transaction transaction = TransactionMapper.toEntity(request, fromAccount, toAccount, typeEnum);
    transaction.setTransactionId(UUID.randomUUID());
    transaction.setCreatedAt(OffsetDateTime.now());

    try {
        transactionRepository.save(transaction);   
    } catch (Exception e) {
        System.out.println(ANSI_RED +"--> Error saving transaction: " + e.getMessage()+ANSI_RESET);
    }

    TransferRequestDto.TransferResponse response = new TransferRequestDto.TransferResponse();
    response.setTransactionId(transaction.getTransactionId());
    response.setInteracReferenceId("INT-" + System.currentTimeMillis());
    response.setStatus("PENDING");
    response.setMessage("Transfer initiated. Recipient will be notified.");
    return response;
}

    public TransferRequestDto.ReceiveMoneyResponse receiveMoney(TransferRequestDto.ReceiveMoneyRequest request) {
        System.out.println(ANSI_PURPLE + "--> receiveMoney() called in bankTransactionService" + ANSI_RESET);
        System.err.println(ANSI_BLUE + "Here is the request: " + request + ANSI_RESET);
        System.out.println("--> Initiating receiveMoney to " + request.getToAccountId() + " from " + request.getFromAccountId() + " amount: " + request.getAmount());

        Account toAccount = accountRepository.findByAccountNumber(request.getToAccountId())
                .orElseThrow(() -> new IllegalArgumentException("Recipient Account not found"));
        System.out.println(ANSI_GREEN + "--> To Account: " + toAccount.getAccountNumber() + ", Balance: " + toAccount.getBalance() + ANSI_RESET);

        BigDecimal requestAmount = BigDecimal.valueOf(request.getAmount());
        System.out.println(ANSI_YELLOW + "--> Requested Amount: " + requestAmount + ANSI_RESET);

        toAccount.setBalance(toAccount.getBalance().add(requestAmount));
        System.out.println(ANSI_RED + "--> New To Account Balance: " + toAccount.getBalance() + ANSI_RESET);

        String typeString = request.getTransactionType();
        TransactionType typeEnum = TransactionType.valueOf(typeString);

        Account fromAccount = accountRepository.findByAccountNumber(request.getFromAccountId())
                .orElseThrow(() -> new IllegalArgumentException("Sender Account not found"));
        System.out.println(ANSI_GREEN + "--> From Account: " + fromAccount.getAccountNumber() + ", Balance: " + fromAccount.getBalance() + ANSI_RESET);

        // Use TransactionMapper to map DTO to entity
        Transaction transaction = TransactionMapper.toEntity(request, fromAccount, toAccount, typeEnum);
        transaction.setTransactionId(UUID.randomUUID());
        transaction.setCreatedAt(OffsetDateTime.now());

        try {
            transactionRepository.save(transaction);
        } catch (Exception e) {
            System.out.println(ANSI_RED + "--> Error saving transaction: " + e.getMessage() + ANSI_RESET);
        }

        TransferRequestDto.ReceiveMoneyResponse response = new TransferRequestDto.ReceiveMoneyResponse();
        response.setTransactionId(transaction.getTransactionId());
        response.setInteracReferenceId("INT-" + System.currentTimeMillis());
        response.setStatus("COMPLETED");
        response.setMessage("Funds received successfully.");
        return response;
}
