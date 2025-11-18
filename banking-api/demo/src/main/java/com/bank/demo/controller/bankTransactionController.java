package com.bank.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bank.demo.Dtos.TransferRequestDto;
import com.bank.demo.Dtos.TransferRequestDto.ReceiveMoneyResponse;
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
        TransferResponse response = transactionService.sendMoney(request);
        return ResponseEntity.status(HttpStatus.OK).body(response); 
    }

    @GetMapping("/receive")
    public ResponseEntity<ReceiveMoneyResponse> receiveMoney(@RequestBody TransferRequestDto.receivePendingRequest request , @RequestHeader ("Authorization") String authHeader) {
        // Extract the token from "Bearer <token>"
        System.out.println("----> /api/bank-transactions/receive endpoint accessed.");
        ReceiveMoneyResponse response = transactionService.handlePendingTransfer(request.getRecipientAccountId(), request.isAccept() );
        return ResponseEntity.status(HttpStatus.OK).body(response);
    }

    @GetMapping("/testConnectedUser")
    public ResponseEntity<String> testConnectedUser(@RequestHeader ("Authorization") String authHeader) {
        // Extract the token from "Bearer <token>"
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String email = authentication.getName(); // comes from JWT subject
        System.out.println("Connected user email from SecurityContext: " + email);
        return ResponseEntity.status(HttpStatus.OK).body("Connected user endpoint is working!");
    }
}
