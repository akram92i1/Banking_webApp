package com.bank.demo.model;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.UUID;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;
@Entity
@Table(name = "banks")
@Getter @Setter
public class Bank {

    @Id
    @GeneratedValue(generator = "uuid2")
    @Column(name = "bank_id", columnDefinition = "uuid")
    private UUID id;

    @Column(name = "bank_name", nullable = false)
    private String bankName;

    @Column(name = "routing_number", unique = true, nullable = false)
    private String routingNumber;

    @Column(name = "swift_code")
    private String swiftCode;

    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> address;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "contact_info")
    private Map<String, Object> contactInfo;

    @Column(name = "created_at")
    private OffsetDateTime createdAt = OffsetDateTime.now();
}

