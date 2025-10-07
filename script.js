const API_URL = "http://127.0.0.1:5000/generate";
const REVIEW_API_URL = "http://127.0.0.1:5000/review_upload";
const DOWNLOAD_API_URL = "http://127.0.0.1:5000/download_pdf";

// --- Function to Generate Software Engineer Prompt ---
function generateSEResume(name, education, experience, skills, projects, goal) {
  const basePrompt = `
  ACT AS A SENIOR SOFTWARE ENGINEER RECRUITER AND RESUME WRITER. Generate a professional, ATS-FRIENDLY resume for a SOFTWARE ENGINEERING INTERN role, using the details provided.
  
  Name: ${name}
  
  OBJECTIVE
  ${goal}
  
  WORK EXPERIENCE AND PROJECTS
  ${experience}
  ${projects}
  
  SKILLS
  ${skills}
  
  COURSES
  ${education}
  
  EDUCATION
  [Include academic details from education]
  
  LEADERSHIP AND ENGAGEMENT
  [Include leadership details from projects/leadership]

  Follow these STRICT rules:
  1. **Content Quality (CRITICAL):** For all experience and project bullet points, apply the "ACHIEVEMENT AMPLIFICATION" method: use **strong action verbs** (e.g., Engineered, Optimized, Designed, Leveraged) and **quantify the impact** with metrics (e.g., 10x, 50%, 90%) to showcase technical results.
  2. **Structure:** Use the EXACT bold headings listed above.
  3. **ATS Format:** Use a single-column, simple, clean format (NO tables, NO columns).
  `;
  return basePrompt;
}

// --- 1. Resume GENERATION Listener (Form 1 - NOW ONLY GENERATES) ---
document.getElementById("resumeForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const name = document.getElementById("name").value;
  const education = document.getElementById("education").value;
  const experience = document.getElementById("experience").value;
  const skills = document.getElementById("skills").value;
  const projects = document.getElementById("projects").value;
  const goal = document.getElementById("goal").value;
  // jobDescription is NOT used here, solving the "unwanted check" issue.

  document.getElementById("result").classList.remove("hidden");
  document.getElementById("resumeOutput").textContent = "Generating Resume...";

  // 1. Generate the initial resume prompt
  const initialPrompt = generateSEResume(name, education, experience, skills, projects, goal);
  
  // API Call 1: Generate Resume Text
  const generationResponse = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: initialPrompt }),
  });

  const generationData = await generationResponse.json();
  let resumeText = generationData.text; 
  document.getElementById("resumeOutput").textContent = resumeText;
  
  // Store generated text for PDF download
  document.getElementById("downloadBtn").setAttribute('data-content', resumeText);
});

// --- 2. Resume REVIEW Listener (Form 2: FILE UPLOAD - NOW ONLY REVIEWS) ---
document.getElementById("reviewForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const resumeFile = document.getElementById("resumeFile").files[0];
    const reviewJobDescription = document.getElementById("reviewJobDescription").value;

    if (!resumeFile) {
        alert("Please select a resume file (PDF).");
        return;
    }
    
    document.getElementById("result").classList.remove("hidden");
    document.getElementById("resumeOutput").textContent = "Uploading and Running ATS Review...";
    
    const formData = new FormData();
    formData.append("resumeFile", resumeFile);
    formData.append("reviewJobDescription", reviewJobDescription);

    // POST to the dedicated file upload endpoint
    const response = await fetch(REVIEW_API_URL, {
        method: "POST",
        body: formData,
    });

    const data = await response.json();
    const reviewText = data.text;
    
    document.getElementById("resumeOutput").textContent = reviewText;
    
    // Store only the review text for PDF download
    document.getElementById("downloadBtn").setAttribute('data-content', reviewText);
});


// --- Download Logic (Triggers Backend PDF Generation) ---
document.getElementById("downloadBtn").addEventListener("click", async () => {
    const contentToDownload = document.getElementById("downloadBtn").getAttribute('data-content');
    if (!contentToDownload || contentToDownload.trim().length < 10) {
        alert("Please generate or review a resume first.");
        return;
    }
    
    const name = document.getElementById("name").value.replace(/\s/g, '_') || 'Report'; 
    const filename = `${name}_Resume_Report.pdf`;

    alert("Generating PDF... this may take a moment.");

    const downloadResponse = await fetch(DOWNLOAD_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: contentToDownload, filename: filename }),
    });

    if (downloadResponse.ok) {
        const blob = await downloadResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } else {
        const errorText = await downloadResponse.text();
        alert(`Failed to create PDF. Server error: ${errorText}`);
    }
});