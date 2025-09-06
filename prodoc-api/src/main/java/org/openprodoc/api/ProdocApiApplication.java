package org.openprodoc.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@EnableConfigurationProperties
@ComponentScan(basePackages = {"org.openprodoc.api", "APIRest"})
public class ProdocApiApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(ProdocApiApplication.class, args);
    }
}