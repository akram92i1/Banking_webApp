package com.bank.demo.controller;

import com.bank.demo.service.PartitionManagementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/partitions")
public class PartitionController {

    @Autowired
    private PartitionManagementService partitionManagementService;

    /**
     * Get current partition status
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getPartitionStatus() {
        try {
            List<String> existingPartitions = partitionManagementService.getExistingPartitions();
            String status = partitionManagementService.getPartitionStatus();
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", status);
            response.put("existingPartitions", existingPartitions);
            response.put("partitionCount", existingPartitions.size());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to get partition status: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Manually trigger partition creation check
     */
    @PostMapping("/create-missing")
    public ResponseEntity<Map<String, Object>> createMissingPartitions() {
        try {
            partitionManagementService.createMissingPartitions();
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Partition check and creation completed successfully");
            response.put("status", partitionManagementService.getPartitionStatus());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to create partitions: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Create partition for specific month
     */
    @PostMapping("/create/{year}/{month}")
    public ResponseEntity<Map<String, Object>> createPartitionForMonth(
            @PathVariable int year, 
            @PathVariable int month) {
        try {
            if (month < 1 || month > 12) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "Invalid month. Must be between 1 and 12.");
                return ResponseEntity.badRequest().body(errorResponse);
            }

            boolean success = partitionManagementService.createPartitionForMonth(year, month);
            
            Map<String, Object> response = new HashMap<>();
            if (success) {
                response.put("message", String.format("Partition for %d/%d created successfully", year, month));
                response.put("status", partitionManagementService.getPartitionStatus());
                return ResponseEntity.ok(response);
            } else {
                response.put("error", String.format("Failed to create partition for %d/%d", year, month));
                return ResponseEntity.internalServerError().body(response);
            }
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Error creating partition: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * List all existing transaction partitions
     */
    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> listPartitions() {
        try {
            List<String> partitions = partitionManagementService.getExistingPartitions();
            
            Map<String, Object> response = new HashMap<>();
            response.put("partitions", partitions);
            response.put("count", partitions.size());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to list partitions: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }
}