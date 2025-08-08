package com.bank.demo.config;

import java.security.Key;
import java.util.Date;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.security.Keys;
import io.jsonwebtoken.security.SignatureException;


//This utility class handles the creation, validation, and extraction of information from JWT tokens.
@Component
public class JwtUtils {
    // The JwtUtils class is responsible for handling JWT operations such as token generation, validation, and parsing.
    private  String SECRET_KEY;
    @Value("${jwt.secret}")
    public void setSecretKey(String secretKey) {
        // This setter will be called by Spring to inject the value
        SECRET_KEY = secretKey;
    }
    private Key getSigningKey(){
        return Keys.hmacShaKeyFor(SECRET_KEY.getBytes());
    }
    @Value("${jwt.expiration}")
    private long EXPIRATION_TIME; 


    //Generate JWT token
    public String generateToken(UUID userId , String email) {
         Date now  =  new Date(); 
         Date expiryDate = new Date(now.getTime() + EXPIRATION_TIME); // 1 day expiration
         return Jwts.builder()
                .setSubject(email)
                .claim("userId", userId.toString())
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }
    // Extract user ID from JWT token
    public UUID getUserIdFromToken(String token) {
        Claims claims = parseToken(token);
        return UUID.fromString(claims.get("userId", String.class));
    }
       // Extract email from token
    public String getEmailFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.getSubject();
    }

    public long getExpirationTime(String token) {
        Claims claims = parseToken(token);
        return claims.getExpiration().getTime();
    }

    // Validate the token
    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (ExpiredJwtException ex) {
            System.out.println("JWT expired");
        } catch (UnsupportedJwtException ex) {
            System.out.println("JWT unsupported");
        } catch (MalformedJwtException ex) {
            System.out.println("JWT malformed");
        } catch (SignatureException ex) {
            System.out.println("Invalid JWT signature");
        } catch (IllegalArgumentException ex) {
            System.out.println("JWT claims string is empty.");
        }
        return false;
    }
    
    // Parse the token and return the claims
    private Claims parseToken(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }
}   
