package com.bank.demo.Dtos;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
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
        private String referenceNumber;
        private String securityQuestion;
        private String securityAnswer; // plain, will be hashed in service
        private String description;
        private OffsetDateTime scheduledAt;
        private BigDecimal feeAmount;
        private BigDecimal exchangeRate; // if cross-currency
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
        public OffsetDateTime getScheduledAt() {
            return scheduledAt;
        }
        public void setScheduledAt(OffsetDateTime scheduledAt) {
            this.scheduledAt = scheduledAt;
        }

        public BigDecimal getFeeAmount() {
            return feeAmount;
        }
        public void setFeeAmount(BigDecimal feeAmount) {
            this.feeAmount = feeAmount;
        }

        public String getReferenceNumber() {
            return referenceNumber;
        }
        public void setReferenceNumber(String referenceNumber) {
            this.referenceNumber = referenceNumber;
        }

        public BigDecimal getExchangeRate() {
            return exchangeRate;
        }
        public void setExchangeRate(BigDecimal exchangeRate) {
            this.exchangeRate = exchangeRate;
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

    public static class ReceiveMoneyRequest {
        private String toAccountId;
        private String fromAccountId; 
        private String interacReferenceId;
        private String securityAnswer; // plain, will be hashed in service
        // Getters and Setters
        public String getToAccountId() {
            return toAccountId;
        }
        public void setToAccountId(String toAccountId) {
            this.toAccountId = toAccountId;
        }
        public String getFromAccountId() {
            return fromAccountId;
        }
        public void setFromAccountId(String fromAccountId) {
            this.fromAccountId = fromAccountId;
        }
        public String getInteracReferenceId() {
            return interacReferenceId;
        }
        public void setInteracReferenceId(String interacReferenceId) {
            this.interacReferenceId = interacReferenceId;
        }
        public String getSecurityAnswer() {
            return securityAnswer;
        }
        public void setSecurityAnswer(String securityAnswer) {
            this.securityAnswer = securityAnswer;
        }
    }

    public static class ReceiveMoneyResponse {
        private UUID transactionId;
        private String status; // PENDING, COMPLETED, FAILED
        private String message;
        private double amount;

        // Getters and Setters
        public UUID getTransactionId() {
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
        public String getMessage() {
            return message;
        }
        public void setMessage(String message) {
            this.message = message;
        }
        public double getAmount() {
            return amount;
        }   
        public void setAmount(double amount) {
            this.amount = amount;
        }
    }

}
