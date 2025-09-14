package com.bank.demo;
import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import static org.mockito.Mockito.when;
import org.mockito.MockitoAnnotations;
import org.springframework.http.ResponseEntity;

import com.bank.demo.Dtos.TransferRequestDto;
import com.bank.demo.Dtos.TransferRequestDto.TransferResponse;
import com.bank.demo.controller.bankTransactionController;
import com.bank.demo.exceptions.InsufficientFundsException;
import com.bank.demo.service.bankTransactionService;

public class banTransactionControllerTest {
    
    @Mock 
    private bankTransactionService transactionService;

    @InjectMocks
    private bankTransactionController controller;

    public banTransactionControllerTest() {
        MockitoAnnotations.openMocks(this);
    }


    @Test
    void testSendMoney() throws InsufficientFundsException {
        TransferRequestDto dto = new TransferRequestDto();
        TransferRequestDto.TransferRequest request = new TransferRequestDto.TransferRequest();
        // set request properties as needed
        TransferRequestDto.TransferResponse mockResponse =  new TransferRequestDto.TransferResponse();
        mockResponse.setStatus("PENDING");
        when(transactionService.sendMoney(request)).thenReturn(mockResponse);
       ResponseEntity responseEntity = controller.sendMoney(request, "Bearer testtoken");
       TransferResponse response = (TransferResponse) responseEntity.getBody();
      assertEquals("PENDING", response.getStatus());
    }      

}
