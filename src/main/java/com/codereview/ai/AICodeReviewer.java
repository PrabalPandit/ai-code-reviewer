package com.codereview.ai;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AICodeReviewer {
    private static final Logger logger = LoggerFactory.getLogger(AICodeReviewer.class);
    private static final String GUIDELINES_PATH;
    private static final String API_KEY;
    private final GeminiAIClient aiClient;
    private final String guidelines;

    static {
        Properties props = new Properties();
        try (InputStream input = AICodeReviewer.class.getClassLoader().getResourceAsStream("application.properties")) {
            if (input == null) {
                throw new RuntimeException("Unable to find application.properties");
            }
            props.load(input);
            GUIDELINES_PATH = props.getProperty("guidelines.path");
            API_KEY = props.getProperty("gemini.api.key");
            if (API_KEY == null || API_KEY.equals("YOUR_API_KEY_HERE")) {
                throw new RuntimeException("Please set your Gemini API key in application.properties");
            }
        } catch (IOException e) {
            throw new RuntimeException("Error loading application.properties", e);
        }
    }

    public AICodeReviewer() throws IOException {
        this.aiClient = new GeminiAIClient(API_KEY);
        this.guidelines = Files.readString(Paths.get(GUIDELINES_PATH));
    }

    public void reviewFile(String sourceFile, String outputFile) throws IOException, InterruptedException {
        logger.info("Starting code review for file: {}", sourceFile);
        
        // Read the source file
        String code = Files.readString(Paths.get(sourceFile));
        
        // Get AI review
        String review = aiClient.reviewCode(code, guidelines);
        
        // Write the review to output file
        Path outputPath = Paths.get(outputFile);
        Files.createDirectories(outputPath.getParent());
        Files.writeString(outputPath, review);
        
        logger.info("Code review completed. Report written to: {}", outputFile);
    }

    public void reviewProject(String projectPath, String outputDir) throws IOException, InterruptedException {
        logger.info("Starting project review for: {}", projectPath);
        
        // Create output directory if it doesn't exist
        Path outputPath = Paths.get(outputDir);
        Files.createDirectories(outputPath);
        
        // Find all Java files in the project
        List<Path> javaFiles = findJavaFiles(Paths.get(projectPath));
        logger.info("Found {} Java files to review", javaFiles.size());
        
        // Review each file and collect results
        List<String> reviews = new ArrayList<>();
        for (Path file : javaFiles) {
            try {
                String code = Files.readString(file);
                String review = aiClient.reviewCode(code, guidelines);
                reviews.add(String.format("=== Review for %s ===\n%s\n", file, review));
            } catch (Exception e) {
                logger.error("Error reviewing file {}: {}", file, e.getMessage());
                reviews.add(String.format("=== Error reviewing %s ===\n%s\n", file, e.getMessage()));
            }
        }
        
        // Write combined review to output file
        String combinedReview = String.join("\n", reviews);
        Path reviewFile = outputPath.resolve("project-review.md");
        Files.writeString(reviewFile, combinedReview);
        
        logger.info("Project review completed. Report written to: {}", reviewFile);
    }

    private List<Path> findJavaFiles(Path root) throws IOException {
        return Files.walk(root)
                .filter(path -> path.toString().endsWith(".java"))
                .filter(path -> !path.toString().contains("/target/"))
                .filter(path -> !path.toString().contains("/test/"))
                .collect(Collectors.toList());
    }
} 