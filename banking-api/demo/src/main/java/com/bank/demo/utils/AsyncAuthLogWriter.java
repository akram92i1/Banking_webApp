package com.bank.demo.utils;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

@Component
public class AsyncAuthLogWriter {
    private static final String LOG_DIR = "logs";
    private static final int BATCH_SIZE = 10;
    private static final int FLUSH_INTERVAL_SECONDS = 5;
    
    private final ObjectMapper objectMapper;
    private final ConcurrentLinkedQueue<Map<String, Object>> logBuffer;
    private final ScheduledExecutorService scheduler;
    
    public AsyncAuthLogWriter() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
        this.objectMapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
        this.logBuffer = new ConcurrentLinkedQueue<>();
        this.scheduler = Executors.newSingleThreadScheduledExecutor();
        System.out.println("AsyncAuthLogWriter initialized successfully!");
    }

    @PostConstruct
    public void startPeriodicFlush() {
        // Schedule periodic flush every 5 seconds
        scheduler.scheduleAtFixedRate(this::flushBuffer, 
            FLUSH_INTERVAL_SECONDS, 
            FLUSH_INTERVAL_SECONDS, 
            TimeUnit.SECONDS);
        System.out.println("Periodic log flush scheduled every " + FLUSH_INTERVAL_SECONDS + " seconds");
    }

    @PreDestroy
    public void shutdown() {
        System.out.println("Shutting down AsyncAuthLogWriter...");
        // Flush any remaining logs before shutdown
        flushBuffer();
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Non-blocking method to queue log entry
     */
    public void writeLogAsync(Map<String, Object> logData) {
        // Add timestamp if not present
        if (!logData.containsKey("timestamp")) {
            logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        }
        
        // Add to buffer (non-blocking)
        logBuffer.offer(new HashMap<>(logData));
        
        // If buffer is full, trigger immediate flush
        if (logBuffer.size() >= BATCH_SIZE) {
            CompletableFuture.runAsync(this::flushBuffer);
        }
    }

    /**
     * Spring @Async method for asynchronous logging
     */
    @Async("authLoggingExecutor")
    public CompletableFuture<Boolean> writeLogAsyncSpring(Map<String, Object> logData) {
        try {
            writeLogSync(logData);
            return CompletableFuture.completedFuture(true);
        } catch (Exception e) {
            System.err.println("Async logging failed: " + e.getMessage());
            return CompletableFuture.completedFuture(false);
        }
    }

    /**
     * Synchronous version for critical logs that must be written immediately
     */
    public void writeLogSync(Map<String, Object> logData) {
        try {
            // Ensure the log directory exists
            File logDir = new File(LOG_DIR);
            if (!logDir.exists()) {
                boolean created = logDir.mkdirs();
                if (!created) {
                    System.err.println("Failed to create log directory!");
                    return;
                }
            }
            
            // Create daily log file name
            String date = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            String fileName = LOG_DIR + "/auth_logs_" + date + ".json";
            File logFile = new File(fileName);
            
            // Read existing logs or create new structure
            Map<String, Object> dailyLogs = readExistingLogs(logFile);
            
            // Add timestamp if not present
            if (!logData.containsKey("timestamp")) {
                logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            
            // Add the new log entry to the logs array
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> logs = (List<Map<String, Object>>) dailyLogs.get("logs");
            logs.add(new HashMap<>(logData));
            
            // Update metadata
            dailyLogs.put("totalEntries", logs.size());
            dailyLogs.put("lastUpdated", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            // Write the updated logs back to file
            writeLogsToFile(fileName, dailyLogs);
            
        } catch (Exception e) {
            System.err.println("Error in writeLogSync method: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Flush all buffered logs to file
     */
    private void flushBuffer() {
        if (logBuffer.isEmpty()) {
            return;
        }

        List<Map<String, Object>> logsToFlush = new ArrayList<>();
        
        // Drain the buffer
        Map<String, Object> logEntry;
        while ((logEntry = logBuffer.poll()) != null) {
            logsToFlush.add(logEntry);
        }

        if (logsToFlush.isEmpty()) {
            return;
        }

        System.out.println("Flushing " + logsToFlush.size() + " log entries to file...");

        try {
            // Ensure the log directory exists
            File logDir = new File(LOG_DIR);
            if (!logDir.exists()) {
                boolean created = logDir.mkdirs();
                if (!created) {
                    System.err.println("Failed to create log directory during flush!");
                    return;
                }
            }
            
            // Create daily log file name
            String date = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            String fileName = LOG_DIR + "/auth_logs_" + date + ".json";
            File logFile = new File(fileName);
            
            // Read existing logs or create new structure
            Map<String, Object> dailyLogs = readExistingLogs(logFile);
            
            // Add all buffered logs
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> logs = (List<Map<String, Object>>) dailyLogs.get("logs");
            logs.addAll(logsToFlush);
            
            // Update metadata
            dailyLogs.put("totalEntries", logs.size());
            dailyLogs.put("lastUpdated", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            // Write the updated logs back to file
            writeLogsToFile(fileName, dailyLogs);
            
            System.out.println("Successfully flushed " + logsToFlush.size() + " log entries");
            
        } catch (Exception e) {
            System.err.println("Error flushing log buffer: " + e.getMessage());
            e.printStackTrace();
            
            // Re-add failed logs back to buffer for retry
            for (Map<String, Object> failedLog : logsToFlush) {
                logBuffer.offer(failedLog);
            }
        }
    }

    // Existing helper methods (same as before)
    private Map<String, Object> readExistingLogs(File logFile) {
        try {
            if (!logFile.exists()) {
                return createNewLogStructure();
            }
            
            if (logFile.length() == 0) {
                return createNewLogStructure();
            }
            
            String content = Files.readString(Paths.get(logFile.getPath()));
            if (content.trim().isEmpty()) {
                return createNewLogStructure();
            }
            
            TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {};
            Map<String, Object> existingLogs = objectMapper.readValue(content, typeRef);
            
            if (!existingLogs.containsKey("logs")) {
                existingLogs.put("logs", new ArrayList<Map<String, Object>>());
            }
            
            return existingLogs;
            
        } catch (Exception e) {
            System.err.println("Error reading existing logs: " + e.getMessage());
            return createNewLogStructure();
        }
    }
    
    private Map<String, Object> createNewLogStructure() {
        Map<String, Object> newDailyLogs = new HashMap<>();
        newDailyLogs.put("date", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")));
        newDailyLogs.put("createdAt", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        newDailyLogs.put("totalEntries", 0);
        newDailyLogs.put("logs", new ArrayList<Map<String, Object>>());
        return newDailyLogs;
    }
    
    private void writeLogsToFile(String fileName, Map<String, Object> dailyLogs) throws IOException {
        String jsonContent = objectMapper.writeValueAsString(dailyLogs);
        
        File file = new File(fileName);
        File parentDir = file.getParentFile();
        if (!parentDir.exists()) {
            parentDir.mkdirs();
        }
        
        try (FileWriter writer = new FileWriter(fileName, false)) {
            writer.write(jsonContent);
            writer.flush();
        }
    }

    // Get current buffer size for monitoring
    public int getBufferSize() {
        return logBuffer.size();
    }
}