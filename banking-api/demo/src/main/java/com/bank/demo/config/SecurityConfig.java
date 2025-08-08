import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import com.bank.demo.config.JwtAuthenticationFilter;
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    private final AuthenticationProvider authenticationProvider ; 
    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public  SecurityConfig(
        JwtAuthenticationFilter jwtAuthenticationFilter ,
        AuthenticationProvider authenticationProvider 
    ) {

        System.out.println("--> SecurityConfig Filter Initialized");
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
        this.authenticationProvider = authenticationProvider; 
    }


     @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .formLogin(form -> form.disable())
            .csrf(csrf -> csrf.disable())
            .httpBasic(basic -> basic.disable()) // <--- disables HTTP Basic Auth
            .sessionManagement(sess -> sess.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
            
        
        http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }
}
