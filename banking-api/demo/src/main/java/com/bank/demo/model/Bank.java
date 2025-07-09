package com.bank.demo.model;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.OffsetDateTime;
import java.util.Map;
import java.util.UUID;

import com.bank.model.converter.JsonConverter;
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

    @Convert(converter = JsonConverter.class)
    private Map<String, Object> address;

    @Convert(converter = JsonConverter.class)
    @Column(name = "contact_info")
    private Map<String, Object> contactInfo;

    @Column(name = "created_at")
    private OffsetDateTime createdAt = OffsetDateTime.now();
}

