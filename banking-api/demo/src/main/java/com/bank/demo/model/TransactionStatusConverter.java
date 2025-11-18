package com.bank.demo.model;

import com.bank.demo.model.enums.TransactionStatus;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter(autoApply = false)
public class TransactionStatusConverter implements AttributeConverter<TransactionStatus, String> {
    
    @Override
    public String convertToDatabaseColumn(TransactionStatus status) {
        System.out.println("Hibernate version: " + org.hibernate.Version.getVersionString());
        return status == null ? null : status.name();
    }

    @Override
    public TransactionStatus convertToEntityAttribute(String dbData) {
        System.out.println("Hibernate version: " + org.hibernate.Version.getVersionString());
        if (dbData == null || dbData.trim().isEmpty()) {
            return null;
        }
        
        try {
            return TransactionStatus.valueOf(dbData.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            System.err.println("Invalid TransactionStatus value from DB: " + dbData);
            return null;
        }
    }
}

// And in your entity:
// @Convert(converter = TransactionStatusConverter.class)
// @Column(name = "transaction_status", insertable = true, updatable = true)
// private TransactionStatus transactionStatus;