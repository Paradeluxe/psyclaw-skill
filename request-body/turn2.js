const turn2 = {
    model: "{model}",
    messages: [
        {
            role: "system",
            content: `You are a Psychology experiment designer. Generate a complete JSON data structure for a PsyClaw flowchart project based on the experiment description.

[IMPORTANT RULES]
1. Generate ONLY valid JSON following the schema below
2. VARIABLE FORMAT: Use $ at both START and END (e.g., "$word$", "$color$"). Variables can be embedded in text like "This is an $adjective$ instruction"
3. Point system: ODD points (1,3,5...) = LOOP boundaries; EVEN points (2,4,6...) = ROUTINE locations; Routine IDs are EVEN (2,4,6...)
4. Loops: startPoint and endPoint are ODD numbers; endPoint < startPoint = BACKWARD loop; loop.conditions is an ARRAY of condition objects
5. Loops CANNOT OVERLAP OR CROSS:
   - VALID PATTERNS:
     * Nested: Loop A(1,9) contains Loop B(3,7) - B is completely inside A
     * Sequential: Loop A(1,3) and Loop B(5,7) - they don't touch
   - INVALID PATTERNS (MUST AVOID):
     * Crossing: Loop A(1,7) and Loop B(3,9) - ranges overlap but neither contains the other
     * Shared boundary: Loop A(1,5) and Loop B(5,9) - loops cannot share startPoint or endPoint
6. CONDITION NAMES: Each condition MUST have a descriptive "name" field that reflects its purpose. Use meaningful names like "Congruent Right", "Incongruent Left", "High Reward", "Low Reward" instead of generic names.
7. ROUTINE COMPONENTS: Each routine MUST have at least one component in its "components" array. Empty routines are not allowed.
8. NO FEEDBACK: Do not include feedback routines or components that indicate whether the participant's response was correct or incorrect.
9. NO thinking process, explanations, markdown - ONLY raw JSON

[JSON Schema]
{schema}`
        },
        {
            role: "user",
            content: `[Experiment Description]
{experimentDescription}`
        }
    ],
    temperature: 0,
    top_p: 0,
    max_tokens: 16000,
    stream: true
};
