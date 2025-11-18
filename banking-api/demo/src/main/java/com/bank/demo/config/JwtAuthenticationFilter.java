package com.bank.demo.config;

import java.io.IOException;

import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.servlet.HandlerExceptionResolver;

import com.bank.demo.service.AuthLoggingService;
import com.bank.demo.service.TokenBlacklistService;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private final TokenBlacklistService tokenBlacklistService;
    private final HandlerExceptionResolver handlerExceptionResolver;
    private final JwtUtils jwtUtils;
    private final UserDetailsService userDetailsService;
    private final AuthLoggingService authLoggingService;

    public JwtAuthenticationFilter(
        JwtUtils jwtUtils,
        UserDetailsService userDetailsService,
        HandlerExceptionResolver handlerExceptionResolver,
        TokenBlacklistService tokenBlacklistService,
        AuthLoggingService authLoggingService 
    ) {
        System.out.println("--> JwtAuthenticationFilter Initialization with Clean Logging.");
        this.jwtUtils = jwtUtils;
        this.userDetailsService = userDetailsService;
        this.handlerExceptionResolver = handlerExceptionResolver;
        this.tokenBlacklistService = tokenBlacklistService;
        this.authLoggingService = authLoggingService;
    }

    @Override
    protected void doFilterInternal(
        @NonNull HttpServletRequest request,
        @NonNull HttpServletResponse response,
        @NonNull FilterChain filterChain
    ) throws ServletException, IOException {

        final String authHeader = request.getHeader("Authorization");
        String clientIP = getClientIpAddress(request);
        String path = request.getServletPath();
        
        System.out.println("----> Client IP: " + clientIP);
        System.out.println("We are inside the doFilterInternal function .. ");
        System.out.println("----> Request path: " + path);
        
        // Skip authentication for public endpoints
        if (path.startsWith("/api/auth/login") || path.startsWith("/api/auth/test") || path.startsWith("/api/auth/logout")) {
            System.out.println("----> Public endpoint accessed: " + path);
            filterChain.doFilter(request, response);
            return;
        }
        
        // Check for missing or invalid Authorization header
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            authLoggingService.logMissingToken(request);
            filterChain.doFilter(request, response);
            return;
        }

        try {
            final String jwt = authHeader.substring(7);
            
            // Check if token is blacklisted
            if (tokenBlacklistService.isTokenBlacklisted(jwt)) {
                System.out.println(">>> Blocked request with blacklisted token");
                authLoggingService.logBlacklistedToken(request);
                
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.getWriter().write("Token has been revoked. Please log in again.");
                return;
            }
            
            final String userEmail = jwtUtils.getEmailFromToken(jwt);
            System.out.println("----> Extracted JWT: " + jwt);
            System.out.println("----> Extracted userEmail from JWT: " + userEmail);
            
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            System.out.println("----> Authentication object: " + authentication);
            
            if (userEmail != null && authentication == null) {
                UserDetails userDetails = this.userDetailsService.loadUserByUsername(userEmail);

                if (jwtUtils.validateToken(jwt)) {
                    UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                            userDetails,
                            null,
                            userDetails.getAuthorities()
                    );

                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                    
                    // Log successful authentication - clean and simple
                    authLoggingService.logAuthenticationSuccess(userEmail, request);
                } else {
                    // Log invalid token - clean and simple
                    authLoggingService.logInvalidToken(userEmail, request);
                }
            }

            filterChain.doFilter(request, response);
            
        } catch (Exception exception) {
            System.out.println("----> Exception in JWT filter: " + exception.getMessage());
            
            // Log authentication error - clean and simple
            authLoggingService.logAuthenticationError(exception.getMessage(), request);
            
            handlerExceptionResolver.resolveException(request, response, null, exception);
        }
    }

    
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedForHeader = request.getHeader("X-Forwarded-For");
        if (xForwardedForHeader == null || xForwardedForHeader.isEmpty()) {
            return request.getRemoteAddr();
        } else {
            return xForwardedForHeader.split(",")[0];
        }
    }
}