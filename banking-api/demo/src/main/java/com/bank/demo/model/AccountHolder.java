package com.bank.demo.model;
import java.time.OffsetDateTime;
import java.util.Map;

import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.EmbeddedId;
import jakarta.persistence.Entity;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.MapsId;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;
@Entity
@Table(name = "account_holders")
@Getter @Setter
public class AccountHolder {

    @EmbeddedId
    private AccountHolderId id;

    @ManyToOne
    @MapsId("accountId")
    @JoinColumn(name = "account_id", nullable = false)
    private Account account;

    @ManyToOne
    @MapsId("userId")
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "relationship")
    private String relationship = "PRIMARY"; // PRIMARY, JOINT, AUTHORIZED_USER

    @Column(name = "permissions", columnDefinition = "jsonb")
    @Convert(converter = JsonToMapConverter.class)
    private Map<String, Object> permissions;

    @Column(name = "added_at")
    private OffsetDateTime addedAt = OffsetDateTime.now();
}
