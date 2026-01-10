package com.bank.demo.Dtos;

import java.util.UUID;

/**
 * Simplified DTO for email-based money transfers (like Interac e-Transfer)
 */
public class EmailTransferRequestDto {
    
    public static class EmailTransferRequest {
        private String recipientEmail;
        private double amount;
        private String description;
        private String transactionType = "INTERAC"; // Default to INTERAC
        private String securityQuestion;
        private String securityAnswer;
        
        // Getters and Setters
        public String getRecipientEmail() {
            return recipientEmail;
        }
        
        public void setRecipientEmail(String recipientEmail) {
            this.recipientEmail = recipientEmail;
        }
        
        public double getAmount() {
            return amount;
        }
        
        public void setAmount(double amount) {
            this.amount = amount;
        }
        
        public String getDescription() {
            return description;
        }
        
        public void setDescription(String description) {
            this.description = description;
        }
        
        public String getTransactionType() {
            return transactionType;
        }
        
        public void setTransactionType(String transactionType) {
            this.transactionType = transactionType;
        }
        
        public String getSecurityQuestion() {
            return securityQuestion;
        }
        
        public void setSecurityQuestion(String securityQuestion) {
            this.securityQuestion = securityQuestion;
        }
        
        public String getSecurityAnswer() {
            return securityAnswer;
        }
        
        public void setSecurityAnswer(String securityAnswer) {
            this.securityAnswer = securityAnswer;
        }
    }
    
    public static class EmailTransferResponse {
        private UUID transactionId;
        private String interacReferenceId;
        private String status;
        private String message;
        private String recipientEmail;
        private double amount;
        
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
        
        public String getRecipientEmail() {
            return recipientEmail;
        }
        
        public void setRecipientEmail(String recipientEmail) {
            this.recipientEmail = recipientEmail;
        }
        
        public double getAmount() {
            return amount;
        }
        
        public void setAmount(double amount) {
            this.amount = amount;
        }
    }
}