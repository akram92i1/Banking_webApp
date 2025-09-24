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
import com.bank.demo.model.enums.TransactionStatus;
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

    public TransferRequestDto.ReceiveMoneyResponse handlePendingTransfer(String recipientAccountId , boolean accept) {
        // Fetch the receipient account (connected user)
        Account recipient  = accountRepository.findByAccountNumber(recipientAccountId)
            .orElseThrow(() -> new IllegalArgumentException("Recipient Account not found")); 
        System.out.println(ANSI_PURPLE +"--> handlePendingTransfer() called in bankTransactionService for recipient: " + recipientAccountId + " transactionId: " + transactionId + " accept: " + accept+ANSI_RESET);

        // Fetch the PENDING  transaction
        Transaction transaction = transactionRepository.findPendingTransactionsByRecipient(UUID.fromString(recipientAccountId), TransactionStatus.PENDING)
            .stream().findFirst()
            .orElseThrow(() -> new IllegalArgumentException("No pending transaction found"));

         // Ensure this transaction is for the recipient
        if (!transaction.getToAccount().getAccountNumber().equals(recipient.getAccountNumber())) {
            throw new SecurityException("This transaction does not belong to the connected user");
        }

        // Ensure it is still pending 
        if (!transaction.getTransactionStatus().equals("PENDING")) {
            throw new IllegalStateException("This transaction is not pending");
        }

        if (accept){
            // Accept: credit recipient account
            recipient.setBalance(recipient.getBalance().add(transaction.getAmount()));
            transaction.setTransactionStatus(TransactionStatus.COMPLETED);
            transaction.setProcessedAt(OffsetDateTime.now());
        }
        else{
             // Decline: refund sender
            Account sender = transaction.getFromAccount();
            sender.setBalance(sender.getBalance().add(transaction.getAmount()));
            transaction.setTransactionStatus(TransactionStatus.CANCELLED);
            transaction.setProcessedAt(OffsetDateTime.now());
        }
        transactionRepository.save(transaction);
        // Build response 
        TransferRequestDto.ReceiveMoneyResponse response = new TransferRequestDto.ReceiveMoneyResponse();
        response.setTransactionId(transaction.getTransactionId());
        if (accept){

            response.setAmount(transaction.getAmount().doubleValue());
            response.setMessage("The amount of "+ transaction.getAmount()+"was deposed to your account ");
        }
        else
        {
            response.setAmount(0.0);
            response.setMessage("Transaction with the amount of"+transaction.getAmount()+"Was canceled");
        }
        response.setStatus(transaction.getTransactionStatus().name());
        response.setMessage(accept ? "Funds received successfully." : "Transfer declined, funds returned.");
        return response;
    }
}
