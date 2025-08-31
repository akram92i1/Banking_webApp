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
import com.bank.demo.model.enums.TransactionStatus;
import com.bank.demo.repository.AccountRepository;
import com.bank.demo.repository.transactionRepository;
@Service
public class bankTransactionService {
    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private transactionRepository transactionRepository;

    public TransferResponse sendMoney(TransferRequest request) throws InsufficientFundsException {
      // 1. Validate account + balance
      Account fromAccount = accountRepository.findByAccountNumber(request.getFromAccountId())
          .orElseThrow(() -> new IllegalArgumentException("Account not found"));
         BigDecimal requestAmount = BigDecimal.valueOf(request.getAmount());
          if(fromAccount.getBalance().compareTo(requestAmount)<0){
                 throw new InsufficientFundsException("Not enough balance to complete transfer");
            }
          fromAccount.setBalance(
            fromAccount.getBalance().subtract(requestAmount)
          );
      
          Account toAccount = accountRepository.findByAccountNumber(request.getFromAccountId())
          .orElseThrow(()-> new IllegalArgumentException("Recipient Account not found"));
        
          Transaction transaction = new Transaction();
          transaction.setTransactionId(UUID.randomUUID());
          transaction.setCreatedAt(OffsetDateTime.now());
          transaction.setFromAccount(fromAccount);
          transaction.setToAccount(toAccount);
          transaction.setAmount(requestAmount);
          transaction.setCurrency(request.getCurrency());
          transaction.setDescription(request.getDescription());
          transaction.setTransactionStatus(TransactionStatus.PENDING);
          transaction.setMerchantInfo(request.getMerchantInfo());
          transactionRepository.save(transaction);
          
      // 4. Trigger notification (email/SMS)
       TransferRequestDto outer = new TransferRequestDto();
       TransferRequestDto.TransferResponse response = outer.new TransferResponse();
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
      TransferRequestDto.TransferResponse response = outer.new TransferResponse();
      response.setTransactionId(transactionID);
      response.setStatus("COMPLETED");
      response.setMessage("Transfer successfully claimed.");
      return response;
    }

     public AutoDepositResponse registerAutoDeposit(AutoDepositRequest request) {
        // Insert into autodeposit_registrations
        TransferRequestDto outer = new TransferRequestDto();
        TransferRequestDto.AutoDepositResponse response = outer.new AutoDepositResponse();
        response.setRegistered(true);
        response.setMessage("Auto-deposit registered successfully.");
        return response;
    }

    public TransferStatusResponse getStatus(UUID transactionId) {
        // Query transactions + interac_transfer_metadata
        TransferRequestDto outer = new TransferRequestDto();
        TransferRequestDto.TransferStatusResponse response = outer.new TransferStatusResponse();
        response.setTransactionId(transactionId);
        response.setStatus("PENDING"); // stub
        response.setAmount(100.00);
        response.setCurrency("CAD");
        return response;
    }
}
