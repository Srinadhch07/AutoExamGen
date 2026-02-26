from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["model_answer", "student_answer"],
    template="""
You are an expert automated grading system.

Compare the student answer with the model answer carefully.

First internally decide correctness.
Then return ONLY valid JSON.
No markdown.
No extra text.

The JSON must be single-line and exactly in this format:
{{"score": 0, "feedback": "short explanation"}}

Scoring:
- 1 = logically correct and matches model answer
- 0 = incorrect or incomplete

Model Answer:
{model_answer}  

Student Answer:
{student_answer}
"""
)