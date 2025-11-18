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

import org.springframework.stereotype.Component;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

@Component
public class AuthLogWriter {
    private static final String LOG_DIR = "logs";
    private final ObjectMapper objectMapper;
    
    public AuthLogWriter() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
        this.objectMapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
        System.out.println("AuthLogWriter initialized successfully!");
    }

    public synchronized void writeLog(Map<String, Object> logData) {
        System.out.println("AuthLogWriter.writeLog() called with data: " + logData);
        
        try {
            // Ensure the log directory exists
            File logDir = new File(LOG_DIR);
            System.out.println("Checking if log directory exists: " + logDir.getAbsolutePath());
            
            if (!logDir.exists()) {
                boolean created = logDir.mkdirs();
                System.out.println("Log directory created: " + created + " at path: " + logDir.getAbsolutePath());
                if (!created) {
                    System.err.println("Failed to create log directory!");
                    return;
                }
            } else {
                System.out.println("Log directory already exists at: " + logDir.getAbsolutePath());
            }
            
            // Create daily log file name
            String date = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            String fileName = LOG_DIR + "/auth_logs_" + date + ".json";
            File logFile = new File(fileName);
            System.out.println("Log file path: " + logFile.getAbsolutePath());
            
            // Read existing logs or create new structure
            Map<String, Object> dailyLogs = readExistingLogs(logFile);
            System.out.println("Current daily logs structure loaded. Total entries before: " + dailyLogs.get("totalEntries"));
            
            // Add timestamp if not present
            if (!logData.containsKey("timestamp")) {
                logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            
            // Add the new log entry to the logs array
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> logs = (List<Map<String, Object>>) dailyLogs.get("logs");
            logs.add(new HashMap<>(logData)); // Create a copy to avoid reference issues
            
            // Update metadata
            dailyLogs.put("totalEntries", logs.size());
            dailyLogs.put("lastUpdated", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            System.out.println("Adding new log entry. Total entries after: " + logs.size());
            
            // Write the updated logs back to file
            boolean success = writeLogsToFile(fileName, dailyLogs);
            if (success) {
                System.out.println("Log successfully written to file: " + fileName);
            } else {
                System.err.println("Failed to write log to file: " + fileName);
            }
            
        } catch (Exception e) {
            System.err.println("Error in writeLog method: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private Map<String, Object> readExistingLogs(File logFile) {
        try {
            System.out.println("Reading existing logs from: " + logFile.getAbsolutePath());
            
            if (!logFile.exists()) {
                System.out.println("Log file doesn't exist, creating new structure");
                return createNewLogStructure();
            }
            
            // Check if file is empty
            if (logFile.length() == 0) {
                System.out.println("Log file is empty, creating new structure");
                return createNewLogStructure();
            }
            
            // Read existing file
            String content = Files.readString(Paths.get(logFile.getPath()));
            System.out.println("File content length: " + content.length());
            
            if (content.trim().isEmpty()) {
                System.out.println("File content is empty, creating new structure");
                return createNewLogStructure();
            }
            
            // Parse existing JSON
            TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {};
            Map<String, Object> existingLogs = objectMapper.readValue(content, typeRef);
            
            // Ensure logs array exists
            if (!existingLogs.containsKey("logs")) {
                System.out.println("Logs array missing, adding empty array");
                existingLogs.put("logs", new ArrayList<Map<String, Object>>());
            }
            
            System.out.println("Successfully read existing logs with " + 
                ((List<?>) existingLogs.get("logs")).size() + " entries");
            
            return existingLogs;
            
        } catch (Exception e) {
            System.err.println("Error reading existing logs: " + e.getMessage());
            e.printStackTrace();
            System.out.println("Falling back to new log structure");
            return createNewLogStructure();
        }
    }
    
    private Map<String, Object> createNewLogStructure() {
        Map<String, Object> newDailyLogs = new HashMap<>();
        newDailyLogs.put("date", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")));
        newDailyLogs.put("createdAt", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        newDailyLogs.put("totalEntries", 0);
        newDailyLogs.put("logs", new ArrayList<Map<String, Object>>());
        System.out.println("Created new log structure for date: " + newDailyLogs.get("date"));
        return newDailyLogs;
    }
    
    private boolean writeLogsToFile(String fileName, Map<String, Object> dailyLogs) {
        try {
            System.out.println("Writing logs to file: " + fileName);
            
            // Convert to JSON
            String jsonContent = objectMapper.writeValueAsString(dailyLogs);
            System.out.println("JSON content generated, length: " + jsonContent.length());
            
            // Ensure parent directory exists
            File file = new File(fileName);
            File parentDir = file.getParentFile();
            if (!parentDir.exists()) {
                boolean created = parentDir.mkdirs();
                System.out.println("Parent directory created: " + created);
            }
            
            // Write to file
            try (FileWriter writer = new FileWriter(fileName, false)) {
                writer.write(jsonContent);
                writer.flush();
            }
            
            // Verify file was written
            File writtenFile = new File(fileName);
            if (writtenFile.exists() && writtenFile.length() > 0) {
                System.out.println("File written successfully. Size: " + writtenFile.length() + " bytes");
                return true;
            } else {
                System.err.println("File write failed - file doesn't exist or is empty");
                return false;
            }
            
        } catch (IOException e) {
            System.err.println("IOException while writing to file: " + e.getMessage());
            e.printStackTrace();
            return false;
        } catch (Exception e) {
            System.err.println("Unexpected error while writing to file: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
    
    // Helper method to get authentication statistics for the day
    public Map<String, Object> getDailyStats(String date) {
        try {
            String fileName = LOG_DIR + "/auth_logs_" + date.replace("-", "") + ".json";
            File logFile = new File(fileName);
            
            if (!logFile.exists()) {
                return new HashMap<>();
            }
            
            Map<String, Object> dailyLogs = readExistingLogs(logFile);
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> logs = (List<Map<String, Object>>) dailyLogs.get("logs");
            
            Map<String, Object> stats = new HashMap<>();
            stats.put("totalRequests", logs.size());
            
            // Count by event types
            Map<String, Integer> eventCounts = new HashMap<>();
            Map<String, Integer> userCounts = new HashMap<>();
            int successCount = 0;
            
            for (Map<String, Object> log : logs) {
                String event = (String) log.get("event");
                Boolean success = (Boolean) log.get("success");
                String username = (String) log.get("username");
                
                eventCounts.put(event, eventCounts.getOrDefault(event, 0) + 1);
                
                if (success != null && success) {
                    successCount++;
                }
                
                if (username != null && !username.equals("unknown")) {
                    userCounts.put(username, userCounts.getOrDefault(username, 0) + 1);
                }
            }
            
            stats.put("successfulAttempts", successCount);
            stats.put("failedAttempts", logs.size() - successCount);
            stats.put("eventBreakdown", eventCounts);
            stats.put("uniqueUsers", userCounts.size());
            stats.put("userActivityBreakdown", userCounts);
            
            return stats;
            
        } catch (Exception e) {
            System.err.println("Error reading daily stats: " + e.getMessage());
            return new HashMap<>();
        }
    }
    
    // Debug method to test logging
    public void testLogging() {
        System.out.println("Testing AuthLogWriter...");
        Map<String, Object> testData = new HashMap<>();
        testData.put("event", "TEST_LOG");
        testData.put("details", "This is a test log entry");
        testData.put("success", true);
        writeLog(testData);
        System.out.println("Test completed.");
    }
}