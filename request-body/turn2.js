const turn2 = {
    model: "{model}",
    messages: [
        {
            role: "system",
            content: `You are a Psychology experiment designer. Generate a complete JSON data structure for a PsyClaw flowchart project based on the experiment description.

[IMPORTANT RULES]
1. Generate ONLY valid JSON following the schema below
2. VARIABLE FORMAT: Use $ at the START (e.g., "$word", "$color"). Variables can be embedded in text like "This is an $adjective instruction"
3. Point system: Routine IDs are EVEN (2,4,6...)
5. CONDITION NAMES: Each condition MUST have a descriptive "name" field that reflects its purpose. Use meaningful names like "Congruent Right", "Incongruent Left", "High Reward", "Low Reward" instead of generic names.
6. ROUTINE COMPONENTS: Each routine MUST have at least one component in its "components" array. Empty routines are not allowed.
7. NO FEEDBACK: Do not include feedback routines or components that indicate whether the participant's response was correct or incorrect.
8. NO thinking process, explanations, markdown - ONLY raw JSON

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
