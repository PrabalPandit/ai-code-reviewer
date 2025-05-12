package com.codereview.ai;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class Main {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage:");
            System.out.println("For single file review:");
            System.out.println("  java -jar ai-code-reviewer.jar <source-file> <output-file>");
            System.out.println("For project review:");
            System.out.println("  java -jar ai-code-reviewer.jar --project <project-path> <output-dir>");
            System.exit(1);
        }

        try {
            AICodeReviewer reviewer = new AICodeReviewer();

            if (args[0].equals("--project")) {
                if (args.length < 3) {
                    System.err.println("Project review requires project path and output directory");
                    System.exit(1);
                }
                String projectPath = args[1];
                String outputDir = args[2];

                if (!Files.exists(Paths.get(projectPath))) {
                    System.err.println("Project directory not found: " + projectPath);
                    System.exit(1);
                }

                reviewer.reviewProject(projectPath, outputDir);
                System.out.println("Project review completed successfully!");
                System.out.println("Review report written to: " + outputDir + "/project-review.md");
            } else {
                String sourceFile = args[0];
                String outputFile = args[1];

                if (!Files.exists(Paths.get(sourceFile))) {
                    System.err.println("Source file not found: " + sourceFile);
                    System.exit(1);
                }

                reviewer.reviewFile(sourceFile, outputFile);
                System.out.println("Code review completed successfully!");
                System.out.println("Review report written to: " + outputFile);
            }

        } catch (IOException | InterruptedException e) {
            System.err.println("Error during code review: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
} 