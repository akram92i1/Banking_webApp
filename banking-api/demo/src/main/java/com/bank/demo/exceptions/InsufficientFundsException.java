package com.bank.demo.exceptions;

public class InsufficientFundsException extends Exception {
    public InsufficientFundsException(String Message) {
        super(Message);
    }
    public InsufficientFundsException(String message, Throwable cause) 
    {
        super(message, cause);
    }
}
