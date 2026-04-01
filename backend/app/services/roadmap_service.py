import json
from datetime import datetime

from fastapi import HTTPException

from app.core.clients import get_groq_client
from app.repositories import roadmaps as roadmap_repository
from app.schemas.roadmap import RoadmapRequest, RoadmapResponse


def _timeline_note_for_grade(grade: str) -> str:
    normalized_grade = str(grade).lower()
    if "9" in normalized_grade or "freshman" in normalized_grade:
        return "Start NOW. Cover 9th and 10th grade in semesters, then 11th/12th in detail."
    if "10" in normalized_grade or "sophomore" in normalized_grade:
        return "Start NOW. Cover the rest of 10th, all of 11th, and end at Jan of 12th Grade."
    if "11" in normalized_grade or "junior" in normalized_grade:
        return "Start NOW. Cover 11th Spring/Summer and 12th Fall/Winter in detail."
    return "Start NOW. Focus on Senior Winter/Spring transition to college."


def _build_prompt(payload: RoadmapRequest) -> str:
    current_date_str = datetime.now().strftime("%B %Y")
    duration_note = _timeline_note_for_grade(payload.grade)

    json_schema = """
    {
      "student_summary": "A warm, personalized paragraph summarizing their profile and unique strengths.",
      "college_list_suggestions": {
         "reach": ["School A with specific major/program", "School B with specific major/program", "School C with specific major/program"],
         "target": ["School C with specific major/program", "School D with specific major/program", "School E with specific major/program"],
         "safety": ["School E with specific major/program", "School F with specific major/program", "School N with specific major/program"]
      },
      "academic_plan": {
         "course_suggestions": ["Specific Course Name (e.g., 'AP Calculus BC' not 'math class')", "Specific Course Name"],
         "testing_strategy": "Specific, actionable advice with target scores, test dates, and preparation timeline"
      },
      "extracurriculars": {
         "current_optimization": "Specific, actionable steps to improve existing activities with measurable outcomes",
         "new_opportunities": ["Specific opportunity name with why it fits (e.g., 'Join Model UN - builds public speaking skills needed for Political Science')", "Specific opportunity 2"]
      },
      "timeline": [
        {
          "period": "Specific Season/Year (e.g., 'Fall 2025' not 'next semester')",
          "focus": "Specific main theme/goal for this period",
          "tasks": ["Specific, actionable task with deadline or timeframe (e.g., 'Register for PSAT by September 15th' not 'take a test')", "Another specific task"]
        }
      ]
    }
    """

    logic_constraints = f"""
    1. TIMELINE CONTEXT: Current date is {current_date_str}. {duration_note}
    2. MANDATORY SECTIONS: Fill every field in the JSON schema.

    3. SPECIFICITY REQUIREMENTS - CRITICAL:
       - All tasks must be SPECIFIC and ACTIONABLE. Use concrete actions, not vague suggestions.
       - Good task: "Register for October PSAT by September 15th through CollegeBoard website"
       - Bad task: "Take a test" or "Study more" or "Do well in school"
       - Include WHO, WHAT, WHEN, WHERE, and HOW when relevant.
       - Each task should have a clear, measurable outcome.

    4. GOAL SPECIFICITY:
       - Course suggestions must include full course names (e.g., "AP Computer Science A" not "a CS class").
       - College suggestions should include the specific major/program (e.g., "MIT - Computer Science and Engineering" not just "MIT").
       - Timeline periods must be specific (e.g., "Fall 2025 - 11th Grade" not "next fall").
       - Testing strategy must include target scores, specific test dates, and preparation methods.

    5. LOCATION STRATEGY:
       - User Preference: "{payload.location}"
       - Prioritize schools in this region with specific major matches.
       - When suggesting schools outside the region, explicitly state why (e.g., "UC Berkeley - #1 in Computer Science, worth considering despite being out of state").

    6. SCHOOL LIST REALISM AND SPECIFICITY:
       - Ensure "Safety" schools are actually safe (typically >50% acceptance or local options).
       - Include specific major/program for each school (e.g., "Arizona State University - Computer Science" not just "ASU").
       - Be cautious with competitive majors. For example, CS at UIUC or UW is very hard, so they are "Targets" or "Reaches" not Safeties.
       - For Art majors, RISD or CalArts are Reaches. Suggest specific state schools with good art programs for Safeties.
       - Include 2-3 schools per category (Reach, Target, Safety) for optimal balance.

    7. TESTING STRATEGY SPECIFICITY:
       - If they are young (9th/10th), provide specific test names (PSAT/NMSQT), registration deadlines, and target scores.
       - If older, provide specific SAT/ACT test dates, registration deadlines, and score goals.
       - Include preparation method recommendations (e.g., "Take 3 practice tests using Khan Academy before October SAT").
       - If test-optional, explain which schools accept this and when they might still want to test.

    8. EXTRACURRICULAR SPECIFICITY:
       - "Current Optimization" should include 2-3 specific, actionable steps to improve existing activities.
       - "New Opportunities" should name specific clubs/organizations and explain why they fit the student's profile.
       - Include leadership opportunities when applicable (e.g., "Run for Debate Team Captain in November").

    9. TIMELINE TASK SPECIFICITY:
       - Each timeline task must include:
         * Specific action verb (Register, Complete, Apply, Join, etc.)
         * What exactly to do (course name, test name, program name)
         * When (deadline or timeframe)
         * Optional: Where (website, location) or How (method)
       - Tasks should be sequenced logically (prerequisites first, then next steps).
       - Include deadlines for time-sensitive items (application deadlines, test registration dates).

    10. HOLISTIC PROFILE CONNECTIONS:
       - Identify connections between interests and suggest interdisciplinary paths.
       - Example: Art + Biology -> Medical Illustration, recommend specific programs.
       - Make connections explicit in the student_summary or task descriptions.
    """

    return (
        "You are a supportive, detail-oriented college admissions mentor. Generate a highly specific, actionable JSON roadmap.\n"
        f"Student Profile:\n"
        f"- Grade: {payload.grade}\n"
        f"- GPA: {payload.gpa}\n"
        f"- Interests: {payload.interests}\n"
        f"- Activities: {payload.activities}\n"
        f"- Demographics: {payload.demographic}\n"
        f"- Testing Status: {payload.testing}\n"
        f"- College Goals: {payload.college_goals}\n"
        f"- Location Preference: {payload.location}\n"
        f"- Course Rigor: {payload.classes}\n\n"
        "### CRITICAL REQUIREMENTS FOR SPECIFICITY\n"
        "Every output must be SPECIFIC and ACTIONABLE. Avoid vague suggestions.\n\n"
        "EXAMPLES OF GOOD VS BAD:\n"
        f"- BAD: 'Take the SAT'\n"
        f"- GOOD: 'Register for October 7th SAT by September 8th via CollegeBoard.org. Aim for 1450+ based on current {payload.gpa} GPA.'\n\n"
        "- BAD: 'Join some clubs'\n"
        "- GOOD: 'Apply to Model UN by September 20th. This builds public speaking skills aligned with your Political Science interest.'\n\n"
        "- BAD: 'Study for tests'\n"
        "- GOOD: 'Complete 3 full-length SAT practice tests using Khan Academy (one per week in September). Review wrong answers thoroughly.'\n\n"
        "### STRATEGIC GUIDELINES\n"
        f"{logic_constraints}\n\n"
        "### OUTPUT INSTRUCTIONS\n"
        "You must output valid JSON using the exact schema below. Fill in EVERY field with SPECIFIC, DETAILED information.\n"
        "Remember: Specificity is key. Each task, suggestion, and recommendation should be concrete and actionable.\n"
        f"{json_schema}"
    )


def _parse_json_response(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": content}


def generate_and_store_roadmap(payload: RoadmapRequest, user_id: str) -> RoadmapResponse:
    prompt = _build_prompt(payload)

    try:
        chat_completion = get_groq_client().chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-only API. You must return valid JSON with all requested fields.",
                },
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        print(f"Groq API Error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="AI service temporarily unavailable.",
        ) from exc

    roadmap_content = chat_completion.choices[0].message.content or "{}"
    roadmap_json = _parse_json_response(roadmap_content)

    try:
        roadmap_id = roadmap_repository.create_roadmap(user_id, payload, roadmap_content)
        return RoadmapResponse(roadmap=roadmap_json, id=roadmap_id)
    except Exception as exc:
        print(f"Database error: {exc}")
        return RoadmapResponse(
            roadmap=roadmap_json,
            warning="Roadmap generated but not saved",
        )
