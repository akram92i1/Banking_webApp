package com.bank.demo.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
@Controller
public class mainController {   

    // This is the main controller for the banking application.
    // It will handle requests and direct them to the appropriate services.
    
    // Add methods to handle requests here, e.g., for account management, transactions, etc.
    @RequestMapping("/")
    public String test () {
        return "test";
    }   

}
// Note: This is a placeholder for the main controller.