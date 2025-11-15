package com.bank.demo.config;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import org.springframework.context.annotation.Bean;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.servlet.HandlerExceptionResolver;

import com.bank.demo.service.TokenBlacklistService;
import com.bank.demo.utils.AuthLogWriter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private final TokenBlacklistService tokenBlacklistService;
    private final HandlerExceptionResolver handlerExceptionResolver;
    private final JwtUtils JwtUtils;
    private final UserDetailsService userDetailsService;
    private final AuthLogWriter authLogWriter;

    public JwtAuthenticationFilter(
        JwtUtils JwtUtils,
        UserDetailsService userDetailsService,
        HandlerExceptionResolver handlerExceptionResolver,
        TokenBlacklistService tokenBlacklistService,
        AuthLogWriter authLogWriter 
    ) {
        System.out.println("--> JwtAuthenticationFilter Initiliazation.");
        this.JwtUtils = JwtUtils;
        this.userDetailsService = userDetailsService;
        this.handlerExceptionResolver = handlerExceptionResolver;
        this.tokenBlacklistService = tokenBlacklistService;
        this.authLogWriter = authLogWriter;
    }

    @Override
    protected void doFilterInternal(
        @NonNull HttpServletRequest request,
        @NonNull HttpServletResponse response,
        @NonNull FilterChain filterChain
    ) throws ServletException, IOException {

        final String authHeader = request.getHeader("Authorization");
        String token = null ; 
        String username = null ; 
        String clientIP = getClientIpAddress(request);
        System.out.println("----> Client IP: " + clientIP);
        String userAgent = request.getHeader("User-Agent");
        String requestMethod = request.getMethod();
        System.out.println("We are inside the doFilterInternal function .. ");
        String path = request.getServletPath();
        System.out.println("----> Request path: " + path);
        
        if (path.startsWith("/api/auth/login") || path.startsWith("/api/auth/test") || path.startsWith("/api/auth/logout")) {
            System.out.println("----> Public endpoint accessed: " + path);
            filterChain.doFilter(request, response);
            return;
        }
        
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            // Log missing token attempt
            Map<String, Object> logData = new HashMap<>();
            logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            logData.put("event", "MISSING_TOKEN");
            logData.put("clientIP", clientIP);
            logData.put("userAgent", userAgent);
            logData.put("requestMethod", requestMethod);
            logData.put("path", path);
            logData.put("success", false);
            logData.put("details", "No Authorization header or invalid format");
            authLogWriter.writeLog(logData);
            
            filterChain.doFilter(request, response);
            return;
        }

        try {
            final String jwt = authHeader.substring(7);
            
            if (tokenBlacklistService.isTokenBlacklisted(jwt)) {
                System.out.println(">>> Blocked request with blacklisted token");
                
                // Log blacklisted token attempt
                Map<String, Object> logData = new HashMap<>();
                logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                logData.put("event", "BLACKLISTED_TOKEN");
                logData.put("clientIP", clientIP);
                logData.put("userAgent", userAgent);
                logData.put("requestMethod", requestMethod);
                logData.put("path", path);
                logData.put("success", false);
                logData.put("details", "Attempt to use blacklisted token");
                authLogWriter.writeLog(logData);
                
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.getWriter().write("Token has been revoked. Please log in again.");
                return;
            }
            
            final String userEmail = JwtUtils.getEmailFromToken(jwt);
            System.out.println("----> Extracted JWT: " + jwt);
            System.out.println("----> Extracted userEmail from JWT: " + userEmail);
            
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            System.out.println("----> Authentication object: " + authentication);
            
            if (userEmail != null && authentication == null) {
                UserDetails userDetails = this.userDetailsService.loadUserByUsername(userEmail);

                if (JwtUtils.validateToken(jwt)) {
                    UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                            userDetails,
                            null,
                            userDetails.getAuthorities()
                    );

                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                    
                    // Log successful authentication
                    Map<String, Object> logData = new HashMap<>();
                    logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                    logData.put("event", "AUTHENTICATION_SUCCESS");
                    logData.put("username", userEmail);
                    logData.put("clientIP", clientIP);
                    logData.put("userAgent", userAgent);
                    logData.put("requestMethod", requestMethod);
                    logData.put("path", path);
                    logData.put("success", true);
                    logData.put("details", "User successfully authenticated");
                    authLogWriter.writeLog(logData);
                } else {
                    // Log invalid token
                    Map<String, Object> logData = new HashMap<>();
                    logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                    logData.put("event", "INVALID_TOKEN");
                    logData.put("username", userEmail);
                    logData.put("clientIP", clientIP);
                    logData.put("userAgent", userAgent);
                    logData.put("requestMethod", requestMethod);
                    logData.put("path", path);
                    logData.put("success", false);
                    logData.put("details", "Token validation failed");
                    authLogWriter.writeLog(logData);
                }
            }

            filterChain.doFilter(request, response);
        } catch (Exception exception) {
            System.out.println("----> Exception in JWT filter: " + exception.getMessage());
            
            // Log authentication exception
            Map<String, Object> logData = new HashMap<>();
            logData.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            logData.put("event", "AUTHENTICATION_ERROR");
            logData.put("clientIP", clientIP);
            logData.put("userAgent", userAgent);
            logData.put("requestMethod", requestMethod);
            logData.put("path", path);
            logData.put("success", false);
            logData.put("details", "Exception during authentication: " + exception.getMessage());
            authLogWriter.writeLog(logData);
            
            handlerExceptionResolver.resolveException(request, response, null, exception);
        }
    }

     @Bean
    CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        configuration.setAllowedOrigins(List.of("http://localhost:8082"));
        configuration.setAllowedMethods(List.of("GET","POST"));
        configuration.setAllowedHeaders(List.of("Authorization","Content-Type"));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();

        source.registerCorsConfiguration("/**",configuration);

        return source;
    }
    
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedForHeader = request.getHeader("X-Forwarded-For");
        if (xForwardedForHeader == null || xForwardedForHeader.isEmpty()) {
            return request.getRemoteAddr();
        }
        else {
            return xForwardedForHeader.split(",")[0];
        }
    }
}