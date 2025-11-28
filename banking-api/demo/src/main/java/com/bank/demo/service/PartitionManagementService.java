package com.bank.demo.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
public class PartitionManagementService {

    private static final Logger logger = LoggerFactory.getLogger(PartitionManagementService.class);
    private static final DateTimeFormatter PARTITION_DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy_MM");
    private static final DateTimeFormatter SQL_DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * Check and create partitions on application startup
     */
    @EventListener(ApplicationReadyEvent.class)
    public void onApplicationReady() {
        logger.info("🚀 Application started - checking transaction partitions...");
        createMissingPartitions();
    }

    /**
     * Scheduled task to check for missing partitions
     * Runs every day at 2 AM
     */
    @Scheduled(cron = "0 0 2 * * ?")
    public void scheduledPartitionCheck() {
        logger.info("⏰ Scheduled partition check starting...");
        createMissingPartitions();
    }

    /**
     * Manual method to create partitions (can be called via endpoint if needed)
     */
    public void createMissingPartitions() {
        try {
            LocalDate currentDate = LocalDate.now();
            
            // Create partitions for current month, next month, and previous month (for safety)
            createPartitionForMonth(currentDate.minusMonths(1)); // Previous month
            createPartitionForMonth(currentDate);                // Current month  
            createPartitionForMonth(currentDate.plusMonths(1));  // Next month
            
            logger.info("✅ Partition check completed successfully");
            
        } catch (Exception e) {
            logger.error("❌ Error during partition management: {}", e.getMessage(), e);
        }
    }

    /**
     * Create a partition for a specific month if it doesn't exist
     */
    private void createPartitionForMonth(LocalDate date) {
        String partitionName = "transactions_" + date.format(PARTITION_DATE_FORMAT);
        
        try {
            // Check if partition already exists
            if (partitionExists(partitionName)) {
                logger.debug("📋 Partition {} already exists", partitionName);
                return;
            }

            // Calculate date range for partition
            LocalDate startDate = date.withDayOfMonth(1);
            LocalDate endDate = startDate.plusMonths(1);
            
            String startDateStr = startDate.format(SQL_DATE_FORMAT);
            String endDateStr = endDate.format(SQL_DATE_FORMAT);

            // Create the partition
            String createPartitionSql = String.format(
                "CREATE TABLE %s PARTITION OF transactions FOR VALUES FROM ('%s') TO ('%s')",
                partitionName, startDateStr, endDateStr
            );

            jdbcTemplate.execute(createPartitionSql);
            logger.info("✨ Created partition: {} for date range {} to {}", 
                       partitionName, startDateStr, endDateStr);

        } catch (Exception e) {
            // Log error but don't fail the application
            logger.error("❌ Failed to create partition {}: {}", partitionName, e.getMessage());
        }
    }

    /**
     * Check if a partition table exists
     */
    private boolean partitionExists(String partitionName) {
        try {
            String checkSql = "SELECT COUNT(*) FROM pg_tables WHERE tablename = ?";
            Integer count = jdbcTemplate.queryForObject(checkSql, Integer.class, partitionName);
            return count != null && count > 0;
        } catch (Exception e) {
            logger.warn("⚠️ Error checking if partition {} exists: {}", partitionName, e.getMessage());
            return false;
        }
    }

    /**
     * Get list of existing partitions (for monitoring/debugging)
     */
    public List<String> getExistingPartitions() {
        try {
            String sql = "SELECT tablename FROM pg_tables WHERE tablename LIKE 'transactions_%' ORDER BY tablename";
            return jdbcTemplate.queryForList(sql, String.class);
        } catch (Exception e) {
            logger.error("❌ Error getting existing partitions: {}", e.getMessage());
            return List.of();
        }
    }

    /**
     * Create partition for a specific month (manual method for admin use)
     */
    public boolean createPartitionForMonth(int year, int month) {
        try {
            LocalDate date = LocalDate.of(year, month, 1);
            createPartitionForMonth(date);
            return true;
        } catch (Exception e) {
            logger.error("❌ Failed to create partition for {}/{}: {}", year, month, e.getMessage());
            return false;
        }
    }

    /**
     * Get partition info for monitoring
     */
    public String getPartitionStatus() {
        try {
            List<String> partitions = getExistingPartitions();
            LocalDate currentDate = LocalDate.now();
            String currentPartition = "transactions_" + currentDate.format(PARTITION_DATE_FORMAT);
            
            boolean currentExists = partitions.contains(currentPartition);
            
            return String.format("Current month partition (%s): %s. Total partitions: %d", 
                                currentPartition, 
                                currentExists ? "EXISTS" : "MISSING", 
                                partitions.size());
        } catch (Exception e) {
            return "Error getting partition status: " + e.getMessage();
        }
    }
}