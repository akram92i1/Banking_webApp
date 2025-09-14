package com.bank.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.Dtos.TransferRequestDto.TransferRequest;
import com.bank.demo.Dtos.TransferRequestDto.TransferResponse;
import com.bank.demo.exceptions.InsufficientFundsException;
import com.bank.demo.service.bankTransactionService;


@RestController
@RequestMapping("/api/bank-transactions")
public class bankTransactionController {

    // This contains endpoints for handling bank transactions such as transfers, deposits, and withdrawals.
    @Autowired 
    private bankTransactionService transactionService;

    @PostMapping("/send")
    public ResponseEntity<TransferResponse> sendMoney(@RequestBody TransferRequest request , @RequestHeader ("Authorization") String authHeader) throws  InsufficientFundsException {
        System.out.println("----> /api/bank-transactions/send endpoint accessed.");
        System.out.println("Request Transaction Type: " + request.getTransactionType());    
        System.out.println("Request From Account ID: " + request.getFromAccountId());
        TransferResponse response = transactionService.sendMoney(request);
        return ResponseEntity.status(HttpStatus.OK).body(response); 
    }
}
