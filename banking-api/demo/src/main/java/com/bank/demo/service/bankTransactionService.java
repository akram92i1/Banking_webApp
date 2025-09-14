package com.bank.demo.service;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.bank.demo.Dtos.TransferRequestDto;
import com.bank.demo.Dtos.TransferRequestDto.AutoDepositRequest;
import com.bank.demo.Dtos.TransferRequestDto.AutoDepositResponse;
import com.bank.demo.Dtos.TransferRequestDto.ClaimRequest;
import com.bank.demo.Dtos.TransferRequestDto.TransferRequest;
import com.bank.demo.Dtos.TransferRequestDto.TransferResponse;
import com.bank.demo.Dtos.TransferRequestDto.TransferStatusResponse;
import com.bank.demo.exceptions.InsufficientFundsException;
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
      // 1. Validate account + balance
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
          fromAccount.setBalance(
            fromAccount.getBalance().subtract(requestAmount)
          );
          System.out.println(ANSI_RED +"--> New From Account Balance: " + fromAccount.getBalance()+ANSI_RESET);
          System.out.println(ANSI_CYAN +"--> Transaction Type: " + request.getTransactionType()+ANSI_RESET);
          // Save the transaction Type as Enum
          String typeString = request.getTransactionType();
          TransactionType typeEnum = TransactionType.valueOf(typeString); // This will throw if the string doesn't match exactly
          //2. Validate receipient account - FIXED BUG     
          Account toAccount = accountRepository.findByAccountNumber(request.getToAccountId())
          .orElseThrow(()-> new IllegalArgumentException("Recipient Account not found"));
          System.out.println(ANSI_GREEN +"--> To Account: " + toAccount.getAccountNumber() + ", Balance: " + toAccount.getBalance()+ANSI_RESET);
          Transaction transaction = new Transaction();
          transaction.setTransactionId(UUID.randomUUID());
          transaction.setCreatedAt(OffsetDateTime.now());
          transaction.setFromAccount(fromAccount);
          transaction.setTransactionType(typeEnum);
          transaction.setToAccount(toAccount);
          transaction.setAmount(requestAmount);
          transaction.setCurrency(request.getCurrency());
          transaction.setDescription(request.getDescription());
          transaction.setMerchantInfo(request.getMerchantInfo());
          try {
           transactionRepository.save(transaction);   
          } catch (Exception e) {
            System.out.println(ANSI_RED +"--> Error saving transaction: " + e.getMessage()+ANSI_RESET);
          }
          
      // 4. Trigger notification (email/SMS)
       TransferRequestDto outer = new TransferRequestDto();
       TransferRequestDto.TransferResponse response = new TransferRequestDto.TransferResponse();
       response.setTransactionId(UUID.randomUUID()); // stub
       response.setInteracReferenceId("INT-" + System.currentTimeMillis());
       response.setStatus("PENDING");
       response.setMessage("Transfer initiated. Recipient will be notified.");
       return response;
    }

    public TransferResponse receiveMoney(UUID transactionID , ClaimRequest claimRequest){
      // 1. Validate security answer
      // 2. Update Transaction -> COMPLETED
      // 3. Credit recipient account
      TransferRequestDto outer = new TransferRequestDto();
      TransferRequestDto.TransferResponse response = new  TransferRequestDto.TransferResponse();
      response.setTransactionId(transactionID);
      response.setStatus("COMPLETED");
      response.setMessage("Transfer successfully claimed.");
      return response;
    }

     public AutoDepositResponse registerAutoDeposit(AutoDepositRequest request) {
        // Insert into autodeposit_registrations
        TransferRequestDto outer = new TransferRequestDto();
        TransferRequestDto.AutoDepositResponse response = new TransferRequestDto.AutoDepositResponse();
        response.setRegistered(true);
        response.setMessage("Auto-deposit registered successfully.");
        return response;
    }

    public TransferStatusResponse getStatus(UUID transactionId) {
        // Query transactions + interac_transfer_metadata
        TransferRequestDto outer = new TransferRequestDto();
        TransferRequestDto.TransferStatusResponse response = new TransferRequestDto.TransferStatusResponse();
        response.setTransactionId(transactionId);
        response.setStatus("PENDING"); // stub
        response.setAmount(100.00);
        response.setCurrency("CAD");
        return response;
    }
}
