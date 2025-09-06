package org.openprodoc.web.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;

@Controller
@RequestMapping("/")
public class LoginController {
    
    private static final Logger logger = LoggerFactory.getLogger(LoginController.class);
    
    @GetMapping({"/", "/index", "/login"})
    public String loginPage(Model model, HttpServletRequest request) {
        HttpSession session = request.getSession(false);
        
        // Check if user is already logged in
        if (session != null && session.getAttribute("User") != null) {
            return "redirect:/main";
        }
        
        model.addAttribute("title", "OpenProdoc - Login");
        return "login";
    }
    
    @PostMapping("/login")
    public String processLogin(
            @RequestParam("User") String username,
            @RequestParam("Password") String password,
            HttpServletRequest request,
            RedirectAttributes redirectAttributes,
            Model model) {
        
        logger.info("Login attempt for user: {}", username);
        
        try {
            // TODO: Integrate with prodoc-api authentication service
            // For now, creating a placeholder authentication
            
            HttpSession session = request.getSession(true);
            
            // Placeholder authentication logic
            if (authenticateUser(username, password)) {
                session.setAttribute("User", username);
                session.setAttribute("LoginTime", System.currentTimeMillis());
                
                logger.info("User {} logged in successfully", username);
                return "redirect:/main";
            } else {
                model.addAttribute("error", "Invalid username or password");
                model.addAttribute("username", username);
                return "login";
            }
            
        } catch (Exception e) {
            logger.error("Login error for user {}: {}", username, e.getMessage());
            model.addAttribute("error", "System error during login. Please try again.");
            model.addAttribute("username", username);
            return "login";
        }
    }
    
    @GetMapping("/logout")
    public String logout(HttpServletRequest request, RedirectAttributes redirectAttributes) {
        HttpSession session = request.getSession(false);
        
        if (session != null) {
            String username = (String) session.getAttribute("User");
            session.invalidate();
            logger.info("User {} logged out", username);
            redirectAttributes.addFlashAttribute("message", "You have been logged out successfully");
        }
        
        return "redirect:/login";
    }
    
    @GetMapping("/main")
    public String mainPage(HttpServletRequest request, Model model) {
        HttpSession session = request.getSession(false);
        
        if (session == null || session.getAttribute("User") == null) {
            return "redirect:/login";
        }
        
        String username = (String) session.getAttribute("User");
        model.addAttribute("username", username);
        model.addAttribute("title", "OpenProdoc - Main");
        
        return "main";
    }
    
    // Placeholder authentication method - will be replaced with prodoc-api integration
    private boolean authenticateUser(String username, String password) {
        // TODO: Replace with actual authentication via prodoc-api
        // For now, accept any non-empty credentials for development
        return username != null && !username.trim().isEmpty() 
               && password != null && !password.trim().isEmpty();
    }
}