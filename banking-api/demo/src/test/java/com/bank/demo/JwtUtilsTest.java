package com.bank.demo;

import java.security.Key;
import java.util.Date;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import com.bank.demo.config.JwtUtils;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;


@ExtendWith(MockitoExtension.class)
public class JwtUtilsTest {
    // The JwtUtils instance we are testing, with mocked dependencies if any.
    @InjectMocks
    private JwtUtils jwtUtils;
    // A fixed secret key for testing purposes. It must be sufficiently long (at least 256 bits or 32 bytes).
    private final String TEST_SECRET = "thisismytestsecretkeyanditisverylongandsecureforjwt";
    // A fixed expiration time for testing (e.g., 1 hour in milliseconds).
    private final long TEST_EXPIRATION_TIME = 3600000; // 1 hour in milliseconds
    @BeforeEach
    public void setUp() {
        // Initialize Mockito annotations for this test class.
        MockitoAnnotations.openMocks(this);
        
        ReflectionTestUtils.setField(jwtUtils, "SECRET_KEY", TEST_SECRET);
        ReflectionTestUtils.setField(jwtUtils, "EXPIRATION_TIME", TEST_EXPIRATION_TIME);
        
        // Ensure the setter for SECRET_KEY is called as it's the actual mechanism for Spring injection.
        // Although ReflectionTestUtils directly sets the field, calling the setter here makes it clearer if the setter logic were more complex.
        jwtUtils.setSecretKey(TEST_SECRET);
    }

    @Test
    void testGetUserIdFromToken_ValidToken() {
        // 1. Arrange: Define a test user ID and email
        UUID expectedUserId = UUID.randomUUID();
        String userEmail = "testuser@example.com";

        // 2. Act: Generate a token using the JwtUtils instance
        String token = jwtUtils.generateToken(expectedUserId, userEmail);

        // 3. Assert: Extract the user ID from the generated token and compare it with the expected ID
        UUID actualUserId = jwtUtils.getUserIdFromToken(token);

        assertNotNull(actualUserId, "The extracted user ID should not be null");
        assertEquals(expectedUserId, actualUserId, "The extracted user ID should match the original user ID");
    }


    @Test
    void testGetUserIdfromToken_ValidToken(){
        // 1. Arrange: Define a test user ID and email
        UUID expectedUserId = UUID.randomUUID();
        String userEmail = "testuser@example.com";
       
        // Manually create a token using the same logic as generateToken for verification
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + TEST_EXPIRATION_TIME);
       
        // Get the signing key using the test secret
        Key signingKey = Keys.hmacShaKeyFor(TEST_SECRET.getBytes());
    }
    
    @Test
    void testGetUserIdFromToken_WithManuallyCreatedToken() {
        // This test case demonstrates extracting from a token created outside the JwtUtils.generateToken method,
        // ensuring the parsing logic is robust.

        // 1. Arrange: Define a test user ID and email
        UUID expectedUserId = UUID.randomUUID();
        String userEmail = "anotheruser@example.com";

        // Manually create a token using the same logic as generateToken for verification
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + TEST_EXPIRATION_TIME);
        
        // Get the signing key using the test secret
        Key signingKey = Keys.hmacShaKeyFor(TEST_SECRET.getBytes());

        String manualToken = Jwts.builder()
                .setSubject(userEmail)
                .claim("userId", expectedUserId.toString())
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(signingKey, SignatureAlgorithm.HS256) // Specify algorithm explicitly
                .compact();

        // 2. Act: Extract the user ID from the manually created token
        UUID actualUserId = jwtUtils.getUserIdFromToken(manualToken);

        // 3. Assert: Compare the extracted user ID with the expected ID
        assertNotNull(actualUserId, "The extracted user ID from manual token should not be null");
        assertEquals(expectedUserId, actualUserId, "The extracted user ID from manual token should match the original");
    }
    @Test
    void testGetUserIdFromToken_InvalidTokenFormat() {
        // 1. Arrange: Provide a token with an invalid format (e.g., just a random string)
        String invalidToken = "thisisnotavalidjwttoken";

        // 2. Act & Assert: Expect an exception when trying to parse an invalid token
        assertThrows(Exception.class, () -> jwtUtils.getUserIdFromToken(invalidToken),
                "Expected an exception for an invalid token format");
    }

    @Test
    void testGetUserIdFromToken_TokenWithoutUserIdClaim() {
        // 1. Arrange: Create a token that intentionally omits the "userId" claim
        String userEmail = "noid@example.com";
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + TEST_EXPIRATION_TIME);
        Key signingKey = Keys.hmacShaKeyFor(TEST_SECRET.getBytes());

        // Token without userId claim
        String tokenWithoutUserId = Jwts.builder()
                .setSubject(userEmail)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();

        // 2. Act & Assert: Expect a NullPointerException or similar as get("userId", String.class) would return null.
        // Depending on Jwts implementation, it might be a NullPointerException or ClassCastException if the default type is not String
        assertThrows(NullPointerException.class, () -> jwtUtils.getUserIdFromToken(tokenWithoutUserId),
                "Expected NullPointerException when 'userId' claim is missing");
    }
    
    // You can add more tests for token expiration, invalid signature, etc., by
    // manipulating the `now` and `expiryDate` or `TEST_SECRET` values.
    // For example:
    @Test
    void testGetUserIdFromToken_ExpiredToken() {
        // 1. Arrange: Generate a token that is already expired
        UUID expectedUserId = UUID.randomUUID();
        String userEmail = "expired@example.com";

        Date past = new Date(System.currentTimeMillis() - 10000); // 10 seconds ago
        Date furtherPast = new Date(System.currentTimeMillis() - 5000); // 5 seconds ago, before 'past'

        Key signingKey = Keys.hmacShaKeyFor(TEST_SECRET.getBytes());

        String expiredToken = Jwts.builder()
                .setSubject(userEmail)
                .claim("userId", expectedUserId.toString())
                .setIssuedAt(furtherPast)
                .setExpiration(past) // Set expiration in the past
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();

        // 2. Act & Assert: Expect ExpiredJwtException when parsing an expired token
        assertThrows(io.jsonwebtoken.ExpiredJwtException.class, () -> jwtUtils.getUserIdFromToken(expiredToken),
                "Expected ExpiredJwtException for an expired token");
    }

}
