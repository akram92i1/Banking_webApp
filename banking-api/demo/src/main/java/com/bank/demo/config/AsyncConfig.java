package com.bank.demo.config;

import java.util.concurrent.Executor;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean(name = "authLoggingExecutor")
    public Executor authLoggingExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        
        // Core pool size - number of threads to keep alive
        executor.setCorePoolSize(2);
        
        // Maximum pool size - maximum number of threads
        executor.setMaxPoolSize(5);
        
        // Queue capacity - how many tasks can be queued
        executor.setQueueCapacity(100);
        
        // Thread name prefix for debugging
        executor.setThreadNamePrefix("AuthLog-");
        
        // What to do when thread pool is exhausted
        executor.setRejectedExecutionHandler(new java.util.concurrent.ThreadPoolExecutor.CallerRunsPolicy());
        
        // Allow threads to time out and be destroyed when not in use
        executor.setAllowCoreThreadTimeOut(true);
        executor.setKeepAliveSeconds(60);
        
        executor.initialize();
        return executor;
    }
}