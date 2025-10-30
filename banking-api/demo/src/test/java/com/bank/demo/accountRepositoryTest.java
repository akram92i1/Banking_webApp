package com.bank.demo;   // ⚠️ doit être le même root package que ton app

import com.bank.demo.model.Account;
import com.bank.demo.repository.AccountRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class accountRepositoryTest {

    @Autowired
    private AccountRepository accountRepository;

    @Test
    void testFindAccountByNumber() {
        Optional<Account> accountOpt = accountRepository.findByAccountNumber("10000001");

        assertThat(accountOpt)
            .as("Account with number 10000001 should exist in DB")
            .isPresent();

        System.out.println(">>> Found account: " + accountOpt.get().getAccountStatus());
    }
}

