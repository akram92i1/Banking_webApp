package com.bank.demo.utils;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class AuthLogWriter {
     private static final String LOG_DIR = "logs" ; // Folder at the project root
     private static final ObjectMapper objectMapper = new ObjectMapper();

     public static void writeLog(Map<String, Object> logData) {
         try {
            // Ensure the log directory exists
             File logDir = new File(LOG_DIR);
             if (!logDir.exists()) {
                 logDir.mkdirs();
             }
             // File name must include timestamp up to minutes to avoid overwriting logs
             String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmm"));
             String fileName = LOG_DIR + "/auth_log_" + timestamp + ".json";
             // Convert log map to JSON string 
             String jsonLog = objectMapper.writeValueAsString(logData);
             // Append log to the file

             try (FileWriter writer = new FileWriter(fileName, true)) {
                 writer.write(jsonLog + System.lineSeparator());
             }
         } catch (IOException e) {
             System.err.println("Error writing authentication log: " + e.getMessage());
         }
     }
}
