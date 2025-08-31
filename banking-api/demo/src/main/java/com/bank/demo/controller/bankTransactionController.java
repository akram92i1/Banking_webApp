package com.bank.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping("/api/bank-transactions")
public class bankTransactionController {

    // This contains endpoints for handling bank transactions such as transfers, deposits, and withdrawals.

    @GetMapping("/test")
    public String getMethodName(@RequestParam String param) {
        return new String("The Transaction is successful with param: " + param);
    }
}
