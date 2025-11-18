package com.bank.demo.responses;

public class LoginResponse {
    private String token;
    private String message;
    private long expirationTime;

    public LoginResponse(String token, String message) {
        this.token = token;
        this.message = message;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public void setExpirationTime(long expirationTime) {
        this.expirationTime = expirationTime;
    }
    
    public long getExpirationTime() {
        return expirationTime;
    }
}
