package com.bank.demo.Dtos;

public class LoginUserDto {
    private String identifier; // can be email OR card number
    private String password;

    // Getters and Setters
    public String getIdentifier() {
        return identifier;
    }

    public void setIdentifier(String identifier) {
        this.identifier = identifier;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}

