package org.openprodoc.web.controller;

import org.openprodoc.web.service.ProdocApiService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;

@Controller
@RequestMapping("/documents")
public class DocumentController {
    
    private static final Logger logger = LoggerFactory.getLogger(DocumentController.class);
    
    @Autowired
    private ProdocApiService apiService;
    
    @GetMapping
    public String documentsPage(
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(defaultValue = "0") int offset,
            HttpServletRequest request,
            Model model) {
        
        HttpSession session = request.getSession(false);
        if (session == null || session.getAttribute("User") == null) {
            return "redirect:/login";
        }
        
        String username = (String) session.getAttribute("User");
        String token = (String) session.getAttribute("Token");
        
        logger.debug("Loading documents for user: {} (limit: {}, offset: {})", username, limit, offset);
        
        // Get documents from API
        ProdocApiService.ApiResponse response = apiService.getDocuments(token, limit, offset);
        
        model.addAttribute("title", "Documents");
        model.addAttribute("username", username);
        model.addAttribute("documentsData", response.getData());
        model.addAttribute("success", response.isSuccess());
        
        if (!response.isSuccess()) {
            model.addAttribute("error", "Failed to load documents: " + response.getData());
        }
        
        return "documents";
    }
    
    @GetMapping("/{id}")
    public String viewDocument(@PathVariable String id, Model model, HttpServletRequest request) {
        HttpSession session = request.getSession(false);
        if (session == null || session.getAttribute("User") == null) {
            return "redirect:/login";
        }
        
        // TODO: Get specific document details
        model.addAttribute("documentId", id);
        model.addAttribute("title", "Document Details");
        
        return "document-details";
    }
    
    @PostMapping("/upload")
    @ResponseBody
    public String uploadDocument(
            @RequestParam("file") String fileName,
            @RequestParam("folderId") String folderId,
            HttpServletRequest request) {
        
        HttpSession session = request.getSession(false);
        if (session == null || session.getAttribute("User") == null) {
            return "{\"success\": false, \"message\": \"Not authenticated\"}";
        }
        
        // TODO: Implement document upload via API
        logger.info("Document upload requested: {} in folder {}", fileName, folderId);
        
        return "{\"success\": true, \"message\": \"Upload functionality will be implemented\"}";
    }
}