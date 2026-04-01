import json

from fastapi import HTTPException

from app.core.clients import get_groq_client
from app.repositories import essays as essay_repository
from app.schemas.essay import EssayRequest, EssayResponse


def _build_prompt(payload: EssayRequest) -> tuple[str, str]:
    word_count = len(payload.essay.split())
    length_instruction = f"Current Word Count: {word_count} words."
    if payload.word_limit:
        length_instruction += f" / Limit: {payload.word_limit} words."
    else:
        length_instruction += " (No specific limit provided)."

    json_schema = """
    {
      "pre_grading_analysis": {
        "cliche_count": 0,
        "cliches_found": ["List phrases"],
        "is_generic_topic": true,
        "predicted_impact": "Will the reader yawn or cry?"
      },
      "scoring_breakdown": {
        "voice_and_authenticity": { "score": 15, "max": 20, "reason": "..." },
        "insight_and_growth": { "score": 15, "max": 20, "reason": "..." },
        "storytelling_and_craft": { "score": 15, "max": 20, "reason": "..." },
        "originality_and_risk": { "score": 15, "max": 20, "reason": "..." },
        "prompt_responsiveness": { "score": 15, "max": 20, "reason": "..." }
      },
      "letter_grade": 75,
      "summary_badge": "Generic & Safe | Risky & Raw | Polished but Boring | Exceptional",
      "key_strengths": ["Strength 1", "Strength 2"],
      "areas_for_improvement": ["Fix 1", "Fix 2"],
      "final_summary": "Summary...",
      "detailed_action_plan": "Specific next steps..."
    }
    """

    system_instruction = f"""
You are a CYNICAL ADMISSIONS OFFICER who is tired of reading generic essays.
Student Context: Grade {payload.grade}, applying to {payload.program}.

### SCORING PROTOCOL (COMPONENT METHOD)
You must grade on 5 distinct components (Max 20 points each).
TOTAL SCORE = Sum of components.

1. Voice & Authenticity (Max 20)
- 18-20: Sounds exactly like a teenager talking to a friend. Raw, vulnerable.
- 14-17: Polished but slightly "resume-speak."
- <14: Sounds like ChatGPT or a parent wrote it.

2. Insight & Growth (Max 20)
- 18-20: A profound realization that changes their worldview.
- 14-17: "I worked hard and succeeded." (Standard)
- <14: No lesson learned, or the lesson is a cliche.

3. Storytelling & Craft (Max 20)
- 18-20: vivid imagery, "Show don't tell," cinematic pacing.
- 14-17: Readable but relies on adjectives ("it was difficult") rather than scenes.
- <14: Confusing structure or boring list of events.

4. Originality & Risk (Max 20)
- 18-20: Topic or angle I have NEVER seen before.
- 14-17: Common topic (sports/mission trip) but with a slight twist.
- <14: The "Costco Rotisserie Chicken" of generic essays (Sports, Dead Pet, Divorce, Moving). CAP THIS AT 12 POINTS IF GENERIC.

5. Prompt Responsiveness (Max 20)
- 18-20: Answers the prompt deeply and directly.
- <14: Ignores the prompt to tell a tangentially related story.

### MANDATORY PENALTIES
- If the essay is a "Sports Injury" or "Mission Trip" essay: Max Total Score is 82 (unless it subverts the genre perfectly).
- If cliches > 3: Deduct 5 points from total.

### GRADE CALIBRATION
- 93+: Top 1% of applicants. (Requires 19/20 in Originality).
- 85-92: Strong, admit-ready.
- 75-84: The "Safe Zone." Good grammar, boring content. MOST ESSAYS ARE HERE.
- < 75: Weak.

DO NOT DEFAULT TO 93. If it feels "fine," give it a 78.
"""

    user_content = f"""
Prompt: {payload.prompt}

{length_instruction}

Student Essay:
{payload.essay}

Analyze and grade based on the component system.
Calculate the 'letter_grade' by summing the 5 component scores.
Output valid JSON:
{json_schema}
"""

    return system_instruction, user_content


def _parse_json_response(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw_text": content}


def generate_and_store_essay_feedback(payload: EssayRequest, user_id: str) -> EssayResponse:
    system_instruction, user_content = _build_prompt(payload)

    try:
        chat_completion = get_groq_client().chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        print(f"Groq API Error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="AI service temporarily unavailable.",
        ) from exc

    feedback_content = chat_completion.choices[0].message.content or "{}"
    feedback_json = _parse_json_response(feedback_content)

    try:
        essay_id = essay_repository.create_essay(user_id, payload, feedback_content)
        return EssayResponse(feedback=feedback_json, id=essay_id)
    except Exception as exc:
        print(f"Database error: {exc}")
        return EssayResponse(
            feedback=feedback_json,
            warning="Feedback generated but not saved",
        )
