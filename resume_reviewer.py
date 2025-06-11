import streamlit as st
from openai import OpenAI
import PyPDF2

# Function to extract text from PDF
def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# GPT-driven evaluation with improved specificity
def evaluate_resume(job_description, resume_text, core_criteria, other_criteria):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Combine criteria into one string
    criteria_prompt = core_criteria.strip()
    prompt = f"""
    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Evaluate the resume strictly based on the job description. \n
    Provide scoring out of 10 with concise bullet points per criteria:
    {criteria_prompt}

    Provide the average of all scores.
    """
    if other_criteria and other_criteria.strip(): 
        prompt += f'Concisely, check if {other_criteria.strip()} available'

    response = client.chat.completions.create(
        model="o3-mini",
        messages=[{"role": "system", "content": "You are an unbiased resume reviewer"},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="Resume Evaluator", layout="wide")
st.title("📑 Resume Evaluator App")

# Input Section
job_description = st.file_uploader("Upload Job Description (PDF)", type="pdf")
uploaded_resumes = st.file_uploader("Upload up to 10 Resumes (PDF)", type="pdf", accept_multiple_files=True)

# Default criteria
default_criteria = """
1. Technical Proficiency
2. Analytical & Problem-Solving
3. Educational & Professional Background
4. Communication & Collaboration
5. Professional Attributes & Industry Experience
""".strip()

# Expandable section for the core criteria (multiline)
crit1 = st.text_area("Core Criteria", value=default_criteria, height=150)

# Single-line input for other criteria
crit2 = st.text_input("Other Criteria", value="")

# Limit resumes to 10
if uploaded_resumes and len(uploaded_resumes) > 10:
    st.warning("You can upload a maximum of 10 resumes.")

# Evaluation button
if st.button("Evaluate Resumes"):
    if not job_description:
        st.error("Please upload the Job Description.")
    elif not uploaded_resumes:
        st.error("Please upload at least one resume.")
    else:
        job_desc_text = extract_text(job_description)

        # Create columns for each resume (max 10 columns)
        columns = st.columns(len(uploaded_resumes[:10]))

        for i, resume in enumerate(uploaded_resumes[:10]):
            resume_text = extract_text(resume)

            # Place each resume's evaluation inside its own column
            with columns[i]:
                with st.expander(f"📄 Evaluation Result for Resume #{i+1}: {resume.name}"):
                    with st.spinner("Evaluating..."):
                        evaluation = evaluate_resume(job_desc_text, resume_text, crit1, crit2)
                        st.markdown(evaluation)
