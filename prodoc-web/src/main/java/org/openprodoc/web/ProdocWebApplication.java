package org.openprodoc.web;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@ComponentScan(basePackages = {"org.openprodoc.web", "OpenProdocServ", "OpenProdocUI"})
public class ProdocWebApplication extends SpringBootServletInitializer {
    
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(ProdocWebApplication.class);
    }
    
    public static void main(String[] args) {
        SpringApplication.run(ProdocWebApplication.class, args);
    }
}