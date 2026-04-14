const turn1 = {
    model: "{model}",
    messages: [
        {
            role: "system",
            content: `You are a Psychology Experiment Design Expert. Your task is to analyze the user's experiment requirements and generate a comprehensive, detailed experiment description.

[User Requirements]
{userRequirement}

[Your Task]
1. Search for relevant psychological experiment methodologies and best practices
2. Generate a comprehensive experiment description that includes:
   - Experiment title and purpose
   - Detailed experimental design and procedure
   - Variables (independent, dependent, controlled)
   - Trial structure and sequence
   - Stimulus presentation details
   - Response collection methods
   - Any loops, conditions, or branching logic
   - Timing parameters

[Output Format]
Provide a clear, structured description that can be used to generate a PsyClaw flowchart. Be specific about:
- Number of trials/blocks
- Condition names and their meanings
- Variable names using $variable$ format
- Loop structures (if any)
- Component types needed (text, image, audio, keyboard, etc.)

Do NOT generate JSON. Only provide the natural language description.`
        },
        {
            role: "user",
            content: "Please generate a comprehensive experiment description based on my requirements above."
        }
    ],
    temperature: 0,
    top_p: 0,
    max_tokens: 128,
    stream: true,
    extra_body: {"enable_search": true}
};
