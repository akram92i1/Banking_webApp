package com.bank.demo.mapper;
import java.math.BigDecimal;

import com.bank.demo.Dtos.TransferRequestDto;
import com.bank.demo.model.Account;
import com.bank.demo.model.Transaction;
import com.bank.demo.model.enums.TransactionType;

public class TransactionMapper {

    // You need to pass Account objects and TransactionType to this method
    public static Transaction toEntity(
        TransferRequestDto.TransferRequest dto,
        Account fromAccount,
        Account toAccount,
        TransactionType transactionType
    ) {
        if (dto == null) {
            return null;
        }

        Transaction transaction = new Transaction();
        transaction.setFromAccount(fromAccount);
        transaction.setToAccount(toAccount);
        transaction.setTransactionType(transactionType);
        transaction.setAmount(BigDecimal.valueOf(dto.getAmount()));
        transaction.setCurrency(dto.getCurrency());
        transaction.setReferenceNumber(dto.getReferenceNumber());
        transaction.setDescription(dto.getDescription());
        transaction.setScheduledAt(dto.getScheduledAt());
        transaction.setFeeAmount(dto.getFeeAmount());
        transaction.setExchangeRate(dto.getExchangeRate());
        transaction.setMerchantInfo(dto.getMerchantInfo());
        // Set other fields as needed

        return transaction;
    }

    public static TransferRequestDto.TransferRequest toDto(Transaction entity) {
        if (entity == null) {
            return null;
        }

        TransferRequestDto.TransferRequest dto = new TransferRequestDto.TransferRequest();
        dto.setFromAccountId(entity.getFromAccount() != null ? entity.getFromAccount().getAccountNumber() : null);
        dto.setToAccountId(entity.getToAccount() != null ? entity.getToAccount().getAccountNumber() : null);
        dto.setTransactionType(entity.getTransactionType() != null ? entity.getTransactionType().name() : null);
        dto.setAmount(entity.getAmount() != null ? entity.getAmount().doubleValue() : 0.0);
        dto.setCurrency(entity.getCurrency());
        dto.setReferenceNumber(entity.getReferenceNumber());
        dto.setDescription(entity.getDescription());
        dto.setScheduledAt(entity.getScheduledAt());
        dto.setFeeAmount(entity.getFeeAmount());
        dto.setExchangeRate(entity.getExchangeRate());
        dto.setMerchantInfo(entity.getMerchantInfo());
        // Set other fields as needed

        return dto;
    }
}