public class SampleClass {
    // TODO: Add proper documentation
    private String password = "secret123"; // Hardcoded credential
    
    public void processData(String input) {
        // No input validation
        String result = "";
        for(int i = 0; i < 1000; i++) {
            result += input; // Inefficient string concatenation
        }
        
        try {
            // Some risky operation
            int value = Integer.parseInt(input);
        } catch(Exception e) {
            // Generic exception handling
        }
    }
    
    // Method is too long and has high cyclomatic complexity
    public void complexMethod(int x) {
        if(x > 0) {
            if(x < 10) {
                if(x % 2 == 0) {
                    if(x % 3 == 0) {
                        if(x % 5 == 0) {
                            System.out.println("Complex condition");
                        }
                    }
                }
            }
        }
    }
} 