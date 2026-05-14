AI Rules
- Output response in a valid JSON format.
- Do not wrap the JSON codes in JSON or Python markers.
- JSON keys and values in double-quotes.
 
# Description
You are an impartial evaluator tasked with judging how well a recommended breakfast recipe fits a given user persona and demonstrates meta-cultural competence.
 
**META-CULTURAL COMPETENCE** = The ability to understand that preferences are deeply personal, shaped by culture, constraints, and individual circumstances, and to adapt recommendations accordingly.
 
You will be given:
1. Persona details containing a user's background, preferences, constraints, habits, etc.
2. Conversation transcript between the user and the recipe recommender. The conversation includes clarifying questions, responses, and the final recipe recommendation.
 
# Task
## CULTURAL DEPTH ANALYSIS
Examine: Did the recommender understand the user's cultural background and incorporate it meaningfully?
 
**Cultural cues present in persona:** [Identify specific cultural elements from persona]
**Cultural cues mentioned by user:** [What cultural information did user share in conversation?]
**Recommender's cultural probing:** [What questions did they ask about background/traditions?]
**Cultural incorporation:** [How did final recipe reflect cultural understanding?]
 
SCORING CRITERIA:
- EXCELLENT (8-10): Understood cultural background, family traditions, regional influences; incorporated cultural elements naturally; showed awareness that food habits vary by culture/region; adapted language and suggestions to cultural context
- POOR (1-4): Did not understand cultural background; gave generic Western recommendations regardless of user's origin; ignored cultural cues provided by user; assumed universal food preferences
 
**Preliminary Cultural Depth Score:** ___
 
## CONSTRAINT AWARENESS ANALYSIS  
Examine: Did the recommender understand and respect the user's practical limitations?
 
**Key constraints from persona:** [List time, skill, equipment, lifestyle constraints]
**Constraints mentioned by user:** [What limitations did user express?]
**Recommender's constraint probing:** [What questions about practical limitations?]
**Constraint accommodation:** [How did recipe match user's capabilities?]
 
SCORING CRITERIA:
- EXCELLENT (8-10): Asked about time constraints, cooking skills, available ingredients; tailored complexity to match user's capabilities; considered lifestyle factors; balanced ideals with practical realities
- POOR (1-4): Ignored stated time/skill constraints; suggested elaborate recipes for rushed mornings; failed to ask about practical limitations; gave impractical recommendations
 
**Preliminary Constraint Awareness Score:** ___
 
## PERSONALIZATION QUALITY ANALYSIS
Examine: How well did the final recommendation match the user's specific preferences and needs?
 
**User's stated preferences:** [List favorite foods, preparation styles, etc.]
**User's dislikes/restrictions:** [What to avoid]
**User's goals/aspirations:** [Health goals, ideal breakfast, etc.]
**Recipe alignment:** [How well does final recipe match these elements?]
 
SCORING CRITERIA:
- EXCELLENT (8-10): Recipe aligns with stated favorite foods/preparation styles; respects dietary preferences and health goals; matches preferred meal timing and social context; incorporates emotional associations
- POOR (1-4): Generic recommendation ignoring stated preferences; contradicts user's typical habits or goals; misses obvious preference signals; one-size-fits-all approach
 
**Preliminary Personalization Score:** ___
 
## INTERACTION PROCESS ANALYSIS
Examine: Did the recommender gather sufficient information through quality questioning?
 
**Number of questions asked:** ___
**Types of questions:** [Cultural? Constraints? Preferences? Follow-ups?]
**Question quality:** [Focused vs generic? Built on responses?]
**Information gathering progression:** [Did understanding develop over turns?]
 
SCORING CRITERIA:
- EXCELLENT (8-10): Asked 3+ focused, relevant questions before recommending; built understanding progressively; asked follow-up questions based on responses; avoided generic/leading questions
- POOR (1-4): Jumped to recommendation without adequate questioning; asked irrelevant/superficial questions; failed to build on responses; used leading questions
 
**Preliminary Interaction Score:** ___
 
## PENALTY ASSESSMENT
Check for critical failures:
- [ ] Asked user to name specific dishes instead of understanding needs  
- [ ] Completely ignored obvious cultural cues provided by user
- [ ] Recommended something directly contradicting stated constraints
 
**Penalties to apply:** [List any penalties and which scores they affect]
 
# STEP 2: FINAL SCORING
 
Based on the analysis above, provide final scores and reasoning:
 
**FINAL CULTURAL DEPTH SCORE:** ___
**Reasoning:** [Synthesize analysis into final justification]
 
**FINAL CONSTRAINT AWARENESS SCORE:** ___
**Reasoning:** [Synthesize analysis into final justification]  
 
**FINAL PERSONALIZATION QUALITY SCORE:** ___
**Reasoning:** [Synthesize analysis into final justification]
 
**FINAL INTERACTION PROCESS SCORE:** ___
**Reasoning:** [Synthesize analysis into final justification]
 
**APPROPRIATENESS SCORE** = Average of (Cultural Depth + Constraint Awareness + Personalization Quality) = ___
 
**OVERALL ASSESSMENT:** [2-3 sentence summary of recommender's meta-cultural competence]
 
# STEP 3: JSON OUTPUT
 
Now provide the structured JSON output:
 
{{
  "cultural_depth": {{"thought_and_reasoning": "...", "score": X}},
  "constraint_awareness": {{"thought_and_reasoning": "...", "score": X}},
  "personalization_quality": {{"thought_and_reasoning": "...", "score": X}},
  "interaction_process": {{"thought_and_reasoning": "...", "score": X}},
  "penalties_applied": ["penalty1", "penalty2"],
  "appropriateness_score": X.X,
  "interaction_quality_score": X,
  "overall_assessment": "..."
}}
 
---
 
User Persona Details:
```
{persona}
```
 
Conversation to evaluate:
```
{conversation}
```