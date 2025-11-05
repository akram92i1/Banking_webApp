package com.bank.demo.config;
import java.io.IOException;
import java.util.List;

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

    public JwtAuthenticationFilter(
        JwtUtils JwtUtils,
        UserDetailsService userDetailsService,
        HandlerExceptionResolver handlerExceptionResolver,
        TokenBlacklistService tokenBlacklistService
    ) {
        System.out.println("--> JwtAuthenticationFilter Initiliazation.");
        this.JwtUtils = JwtUtils;
        this.userDetailsService = userDetailsService;
        this.handlerExceptionResolver = handlerExceptionResolver;
        this.tokenBlacklistService = tokenBlacklistService;
    }

    @Override
    protected void doFilterInternal(
        @NonNull HttpServletRequest request,
        @NonNull HttpServletResponse response,
        @NonNull FilterChain filterChain
    ) throws ServletException, IOException {

        final String authHeader = request.getHeader("Authorization");
        System.out.println("We are inside the doFilterInternal function .. ");
        String path = request.getServletPath();
        System.out.println("----> Request path: " + path);
        if (path.startsWith("/api/auth/login") || path.startsWith("/api/auth/test") || path.startsWith("/api/auth/logout")) {
            System.out.println("----> Public endpoint accessed: " + path);
            filterChain.doFilter(request, response);
            return;
        }
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        try {
            final String jwt = authHeader.substring(7);
            if (tokenBlacklistService.isTokenBlacklisted(jwt)) {
                 System.out.println(">>> Blocked request with blacklisted token");
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
                }
            }

            filterChain.doFilter(request, response);
        } catch (Exception exception) {
            System.out.println("----> Exception in JWT filter: " + exception.getMessage());
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
}