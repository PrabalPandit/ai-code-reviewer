package com.codereview.ai;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.ObjectMapper;

public class GeminiAIClient {
    private static final Logger logger = LoggerFactory.getLogger(GeminiAIClient.class);
    private static final String GEMINI_API_URL;
    private final String apiKey;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    static {
        Properties props = new Properties();
        try (InputStream input = GeminiAIClient.class.getClassLoader().getResourceAsStream("application.properties")) {
            if (input == null) {
                throw new RuntimeException("Unable to find application.properties");
            }
            props.load(input);
            GEMINI_API_URL = props.getProperty("gemini.api.url");
        } catch (IOException e) {
            throw new RuntimeException("Error loading application.properties", e);
        }
    }

    public GeminiAIClient(String apiKey) {
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }

    public String reviewCode(String code, String guidelines) throws IOException, InterruptedException {
        String prompt = buildPrompt(code, guidelines);
        Map<String, Object> requestBody = new HashMap<>();
        Map<String, Object> content = new HashMap<>();
        content.put("parts", new Object[]{Map.of("text", prompt)});
        requestBody.put("contents", new Object[]{content});

        String requestBodyJson = objectMapper.writeValueAsString(requestBody);
        
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(GEMINI_API_URL + "?key=" + apiKey))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestBodyJson))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() != 200) {
            logger.error("Error from Gemini API: {}", response.body());
            throw new IOException("Failed to get response from Gemini API: " + response.statusCode());
        }

        return parseResponse(response.body());
    }

    private String buildPrompt(String code, String guidelines) {
        return "Please review the following Java code according to these guidelines:\n\n" +
               guidelines + "\n\n" +
               "Code to review:\n" +
               code + "\n\n" +
               "Please provide a detailed code review that:\n" +
               "1. Identifies any violations of the guidelines\n" +
               "2. Suggests improvements\n" +
               "3. Highlights potential security issues\n" +
               "4. Notes any performance concerns\n" +
               "5. Provides specific recommendations for each issue\n\n" +
               "Format the response as a structured review with clear sections for each type of issue.";
    }

    private String parseResponse(String responseJson) throws IOException {
        Map<String, Object> response = objectMapper.readValue(responseJson, Map.class);
        // Extract the generated text from the response
        // This is a simplified version - you might need to adjust based on the actual response structure
        return response.toString();
    }
} 