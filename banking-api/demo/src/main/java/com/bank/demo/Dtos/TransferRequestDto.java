package com.bank.demo.Dtos;

import java.util.Map;
import java.util.UUID;

public class TransferRequestDto {

    // Fields for the transfer money request
    public static class TransferRequest{
        private String fromAccountId;
        private String toAccountId; 
        private String recipientEmail;
        private String recipientphoneNumber;
        private String transactionType; // "INTERAC", "INTERNAL"
        private double amount;
        private String currency;
        private String securityQuestion;
        private String securityAnswer; // plain, will be hashed in service
        private String description;
        private Map<String, Object> merchantInfo;

        // Getters and Setters
        public String getFromAccountId() {
            return fromAccountId;
        }
        
        public void setFromAccountId(String fromAccountId) {
            this.fromAccountId = fromAccountId;
        }

        public String getTransactionType() {
            return transactionType;
        }

        public void setTransactionType(String transactionType) {
            this.transactionType = transactionType;
        }

        public String getToAccountId() {
            return toAccountId;
        }
        public void setToAccountId(String toAccountId) {
            this.toAccountId = toAccountId;
        }

        public double getAmount() {
            return amount;
        }
        public void setAmount(double amount) {
            this.amount = amount;
        }
        public String getCurrency() {
            return currency;
        }
        public void setCurrency(String currency) {
            this.currency = currency;
        }
        public String getDescription() {
            return description;
        }
        public void setDescription(String description) {
            this.description = description;
        }
        public Map<String, Object> getMerchantInfo() {
            return merchantInfo;
        }
        public void setMerchantInfo(Map<String, Object> merchantInfo) {
            this.merchantInfo = merchantInfo;
        }
    }

    // Claim transfer
    public static class ClaimRequest {
        private String recipientEmail;
        private String securityAnswer;
    }

    // Register auto-deposit
    public static class AutoDepositRequest {
        private UUID userId;
        private UUID accountId;
        private String email;
        private String phoneNumber;

        // Getters and Setters
        public UUID getUserId() {
            return userId;
        }
        public void setUserId(UUID userId) {
            this.userId = userId;
        }
        public UUID getAccountId() {
            return accountId;
        }
        public void setAccountId(UUID accountId) {
            this.accountId = accountId;
        }
        public String getEmail() {
            return email;
        }
        public void setEmail(String email) {
            this.email = email;
        }
        public String getPhoneNumber() {
            return phoneNumber;
        }
        public void setPhoneNumber(String phoneNumber) {
            this.phoneNumber = phoneNumber;
        }

    }

    // Responses 
    public static class  TransferResponse{
        private UUID transactionId;
        private String interacReferenceId;
        private String status; // PENDING, COMPLETED, FAILED
        private String message;

        // Getters and Setters
        public UUID getTransactionId() {
            return transactionId;       
        }
        public void setTransactionId(UUID transactionId) {
            this.transactionId = transactionId;
        }
        public String getInteracReferenceId() {
            return interacReferenceId;
        }
        public void setInteracReferenceId(String interacReferenceId) {
            this.interacReferenceId = interacReferenceId;       
        }
        public String getStatus() {
            return status;
        }
        public void setStatus(String status) {
            this.status = status;
        }
        public String getMessage() {
            return message;
        }
        public void setMessage(String message) {
            this.message = message;
        }
    }

    public static class AutoDepositResponse {
        private boolean registred ; 
        private String message;
        // Getters and Setters
        public boolean isRegistered() {
            return registred;
        }
        public void setRegistered(boolean registred) {
            this.registred = registred;
        }
        public String getMessage() {
            return message;
        }
        public void setMessage(String message) {
            this.message = message;
        }
    }

    public static class TransferStatusResponse {
    private UUID transactionId;
    private String status;
    private Double amount;
    private String currency;

    // Getters and Setters
    public  UUID getTransactionId() {
        return transactionId;
     }
    
    public void setTransactionId(UUID transactionId) {
        this.transactionId = transactionId;
    }
    public String getStatus() {
        return status;
    }
    public void setStatus(String status) {
        this.status = status;
    }
    public Double getAmount() {
        return amount;
    }
    public void setAmount(Double amount) {
        this.amount = amount;
    }
    public String getCurrency() {
        return currency;
    }
    public void setCurrency(String currency) {
        this.currency = currency;
    }
}    

}
