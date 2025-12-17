package com.bank.demo.service;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import com.bank.demo.Dtos.TransferRequestDto;
import com.bank.demo.Dtos.TransferRequestDto.TransferRequest;
import com.bank.demo.Dtos.TransferRequestDto.TransferResponse;
import com.bank.demo.exceptions.InsufficientFundsException;
import com.bank.demo.model.Account;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.enums.TransactionStatus;
import com.bank.demo.model.enums.TransactionType;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.transactionRepository;
import com.bank.demo.repository.Userepository;
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

    @Autowired
    private Userepository userRepository;

    public TransferResponse sendMoney(TransferRequest request) throws InsufficientFundsException {
        System.out.println(ANSI_PURPLE +"--> sendMoney() called in bankTransactionService (Email-based)"+ANSI_RESET);
        System.err.println(ANSI_BLUE+"Here is the request: " + request+ANSI_RESET);
        
        // Get the authenticated user's email (the sender)
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null) {
            throw new IllegalStateException("User is not authenticated");
        }
        
        String senderEmail = authentication.getName(); // this comes from the JWT subject    
        if (senderEmail == null || senderEmail.trim().isEmpty()) {
            throw new IllegalStateException("Authentication user email is null or empty");
        }
        
        System.out.println(ANSI_GREEN +"--> Authenticated sender email: " + senderEmail+ANSI_RESET);
        
        // Validate required fields
        if (request.getRecipientEmail() == null || request.getRecipientEmail().trim().isEmpty()) {
            throw new IllegalArgumentException("Recipient email is required");
        }
        if (request.getAmount() <= 0) {
            throw new IllegalArgumentException("Amount must be greater than 0");
        }
        if (request.getTransactionType() == null || request.getTransactionType().trim().isEmpty()) {
            throw new IllegalArgumentException("Transaction type is required");
        }
        
        System.out.println("--> Initiating email-based transfer from " + senderEmail + " to " + request.getRecipientEmail() + " amount: " + request.getAmount());
        
        // Find sender's primary account
        Account fromAccount = accountRepository.findPrimaryAccountByUserEmail(senderEmail)
            .orElseThrow(() -> new IllegalArgumentException("Sender account not found for email: " + senderEmail));
        System.out.println(ANSI_GREEN +"--> From Account: " + fromAccount.getAccountNumber() + ", Balance: " + fromAccount.getBalance()+ANSI_RESET);

        // Find recipient's primary account
        Account toAccount = accountRepository.findPrimaryAccountByUserEmail(request.getRecipientEmail())
            .orElseThrow(() -> new IllegalArgumentException("Recipient account not found for email: " + request.getRecipientEmail()));
        System.out.println(ANSI_GREEN +"--> To Account: " + toAccount.getAccountNumber() + ", Balance: " + toAccount.getBalance()+ANSI_RESET);

        BigDecimal requestAmount = BigDecimal.valueOf(request.getAmount());
        System.out.println(ANSI_YELLOW +"--> Requested Amount: " + requestAmount +ANSI_RESET);

        // Prevent self-transfer 
        if (senderEmail.equalsIgnoreCase(request.getRecipientEmail())){
            throw new IllegalArgumentException("Cannot transfer to yourself");
        }

        // Check balance
        if(fromAccount.getBalance().compareTo(requestAmount) < 0){
            throw new InsufficientFundsException("Insufficient funds. Available balance: " + fromAccount.getBalance());
        }

        // Deduct amount from sender's account
        fromAccount.setBalance(fromAccount.getBalance().subtract(requestAmount));
        System.out.println(ANSI_RED +"--> New From Account Balance: " + fromAccount.getBalance()+ANSI_RESET);

        // Save updated account balance
        accountRepository.save(fromAccount);

        // Parse transaction type
        TransactionType typeEnum;
        try {
            typeEnum = TransactionType.valueOf(request.getTransactionType().toUpperCase());
            System.out.println(ANSI_CYAN +"--> Transaction Type: " + typeEnum +ANSI_RESET);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Invalid transaction type: " + request.getTransactionType());
        }

        // Create transaction entity
        Transaction transaction = new Transaction();
        transaction.setTransactionId(UUID.randomUUID());
        transaction.setFromAccount(fromAccount);
        transaction.setToAccount(toAccount);
        transaction.setTransactionType(typeEnum);
        transaction.setAmount(requestAmount);
        transaction.setDescription(request.getDescription() != null ? request.getDescription() : "Email transfer to " + request.getRecipientEmail());
        transaction.setTransactionStatus(TransactionStatus.PENDING); // Pending for recipient approval
        transaction.setCreatedAt(OffsetDateTime.now());

        try {
            transactionRepository.save(transaction);   
            System.out.println(ANSI_GREEN +"--> Transaction saved successfully with ID: " + transaction.getTransactionId()+ANSI_RESET);
        } catch (Exception e) {
            System.out.println(ANSI_RED +"--> Error saving transaction: " + e.getMessage()+ANSI_RESET);
            // Rollback account balance change
            fromAccount.setBalance(fromAccount.getBalance().add(requestAmount));
            accountRepository.save(fromAccount);
            throw new RuntimeException("Failed to save transaction: " + e.getMessage());
        }

        // Build response
        TransferRequestDto.TransferResponse response = new TransferRequestDto.TransferResponse();
        response.setTransactionId(transaction.getTransactionId());
        response.setInteracReferenceId("INT-" + System.currentTimeMillis());
        response.setStatus("PENDING");
        response.setMessage("Transfer initiated successfully. " + request.getRecipientEmail() + " will be notified to accept the transfer.");
        
        return response;
    }

    public TransferRequestDto.ReceiveMoneyResponse handlePendingTransfer(String recipientAccountId , boolean accept) {
        // Fetch the receipient account (connected user)
        Account recipient  = accountRepository.findById(UUID.fromString(recipientAccountId))
            .orElseThrow(() -> new IllegalArgumentException("Recipient Account not found")); 
        System.out.println(ANSI_PURPLE +"--> handlePendingTransfer() called in bankTransactionService for recipient: " + recipientAccountId  + " accept: " + accept+ANSI_RESET);

        // Fetch the PENDING  transaction
        Transaction transaction = transactionRepository.findPendingTransactionsByRecipient(UUID.fromString(recipientAccountId), TransactionStatus.PENDING)
            .stream().findFirst()
            .orElseThrow(() -> new IllegalArgumentException("No pending transaction found"));
        // check the PENDING transaction
        System.out.println(ANSI_GREEN +"--> Found pending transaction: " + transaction.getTransactionId() + " amount: " + transaction.getAmount()+ANSI_RESET + " transaction status: " + transaction.getTransactionStatus());
        
        System.out.println("Type of status: " + transaction.getTransactionStatus().getClass().getName());
         // Ensure this transaction is for the recipient
        if (!transaction.getToAccount().getAccountNumber().equals(recipient.getAccountNumber())) {
            throw new SecurityException("This transaction does not belong to the connected user");
        }

        // Ensure it is still pending 
        if (transaction.getTransactionStatus() != TransactionStatus.PENDING) {
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
