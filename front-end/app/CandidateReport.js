import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { jsPDF } from "jspdf";


/* each card */ 
const cardStyle = {
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 24px rgba(77, 7, 239, 0.1)',
    padding: '16px',
    marginBottom: '20px',
    maxWidth: '900px',
};

/* top banner */
const bannerHeader = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-start',
    backgroundColor: '#FFFFFF',
    color: 'white',
    padding: '8px 24px',            
    width: '100%',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    height: '60px',                
};

/* pairwise logo */ 
const bannerLogo = {
    width: '200px',                
    height: 'auto',
    marginRight: '16px',
};


const candidateHeaderContainer = {
  display: 'flex',
  justifyContent: 'space-between',
  gap: '30px',
  alignItems: 'center',
  marginTop: '30px',
  maxWidth: '1500',
};

const profilePicStyle = {
  width: '80px',
  height: '80px',
  borderRadius: '50%',
  backgroundColor: '#6266f1',
  color: 'white',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '24px',
  fontWeight: 'bold',
  textTransform: 'uppercase',
};

const candidateInfoContainer = {
  flex: 1,
  minWidth: '500px',
};

const buttonGroupStyle = {
  display: 'flex',
  gap: '10px',
};

const downloadButtonStyle = {
  backgroundColor: 'white',
  color: '#6266f1',
  border: '2px solid #6266f1',
  padding: '12px 24px',
  borderRadius: '6px',
  fontWeight: 'bold',
  fontSize: '16px',
  cursor: 'pointer',
};

const scheduleButtonStyle = {
  backgroundColor: '#6266f1',
  color: 'white',
  border: 'none',
  padding: '12px 24px',
  borderRadius: '6px',
  fontWeight: 'bold',
  fontSize: '16px',
  cursor: 'pointer',
};



const transcriptStyle = {
    marginTop: '20px',
    padding: '16px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 24px rgba(77, 7, 239, 0.1)',
    maxWidth: '1050px',
};

const pageStyle = {
    backgroundColor: '#f5f5f5',
    fontFamily: 'Arial, sans-serif',
    padding: '20px',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    /*alignItems: 'center', */ 
};

const buttonStyle = {
    backgroundColor: '#6007ef',  
    color: '#fff',              
    fontSize: '16px',           
    padding: '10px 20px',       
    border: 'none',              
    borderRadius: '0',           
    cursor: 'pointer',           
    marginTop: '20px',          
};

/* box with scores and progress bars */ 
const progressBarContainer = {
    width: '100%',
    backgroundColor: '#eee',
    borderRadius: '5px',
    height: '10px',
    marginTop: '4px',
    marginBottom: '12px',
};

const getScoreColor = (score) => {
    if (score < 5) return '#E74C3C';     // Red
    if (score < 8.0) return '#FFD796';   // Orange
    return '#558F8E';                    // Green
};

const getProgressBarStyle = (score) => ({
    width: `${score * 10}%`,
    backgroundColor: getScoreColor(score),
    height: '100%',
    borderRadius: '5px',
});


// custom icon components for 5 key points 
const CheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="#28a745" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
    <path d="M6.00039 10.7998L2.80039 7.5998L1.86606 8.53314L6.00039 12.6665L15.0004 3.6665L14.0671 2.73314L6.00039 10.7998Z" />
  </svg>
);

const CrossIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="#dc3545" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
    <path d="M9.41 8l3.3-3.29a1 1 0 10-1.42-1.42L8 6.59l-3.29-3.3a1 1 0 00-1.42 1.42L6.59 8l-3.3 3.29a1 1 0 101.42 1.42L8 9.41l3.29 3.3a1 1 0 001.42-1.42L9.41 8z" />
  </svg>
);



const CandidateReport = () => {
    const { interviewId } = useParams();
    const [scores, setScores] = useState([]);
    const [transcript, setTranscript] = useState([]);
    const [showTranscript, setShowTranscript] = useState(false);
    const [summary, setSummary] = useState('');
    const [finalScore, setFinalScore] = useState(null);
    const [candidateName, setCandidateName] = useState('');
    const [candidateLastName, setCandidateLastName] = useState('');
    const [jobTitle, setJobTitle] = useState('');
    const [report, setReport] = useState(null);



    useEffect(() => {
        axios.get(`/api/interview/${interviewId}/details/`)
            .then(res => {setSummary(res.data.summary);
                           setFinalScore(res.data.final_score);
                           setCandidateName(res.data.candidate_name);
                           setCandidateLastName((res.data.candidate_lastname))
                           setJobTitle(res.data.job_title);})
            .catch(err => console.error('Error fetching interview details:', err));

        axios.get(`/api/interviews/${interviewId}/report/`)
            .then(res => setReport(res.data))
            .catch(err => console.error('Error fetching interview report:', err));
    
        axios.get(`/api/scores/${interviewId}`)
            .then(res => setScores(res.data))
            .catch(err => console.error('Error fetching scores:', err));
    
        axios.get(`/api/transcripts/?interview_id=${interviewId}`)
            .then(res => setTranscript(res.data))
            .catch(err => console.error('Error fetching transcript:', err));
    }, [interviewId]);


    {/* function to handle downloading candidate report */}
    const handleDownloadPDF = () => {
        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.getWidth();
        const margin = 20;
        const textWidth = pageWidth - margin * 2;
        let y = 30;

        doc.setFontSize(16);
        doc.text("Interview Report for "+ candidateName, margin, 20);

        doc.setFontSize(10);

        if (report) {
            doc.text(`Recommendation: ${report.recommendation}`, margin, y); y += 10;
            doc.text(`Reason: ${report.reason}`, margin, y); y += 10;

            doc.text("Resume Summary:", margin, y); y += 10;
            doc.text(doc.splitTextToSize(report.resume_summary || '', textWidth), margin, y); y += 30;

            doc.text("Interview Summary:", margin, y); y += 10;
            doc.text(doc.splitTextToSize(report.interview_summary || '', textWidth), margin, y); y += 30;

            doc.text("Key Insights:", margin, y); 
            y += 8;

            report.key_insights.forEach((insight) => {

            // split the text to fit within page
            const wrappedLines = doc.splitTextToSize(insight.text, textWidth - 10);

            // Indented wrapped lines
            wrappedLines.forEach((line) => {
                doc.text("    " + line, margin, y); 
                y += 6;
            });

            y += 4; // spacing between insights
            });
        }

        doc.save(`${candidateName}_${candidateLastName}_report.pdf`);
        };




return (
        <div>
            {/* banner and logo */}
            <div style={bannerHeader}>
                <img src="/static/logo.png" alt="Company Logo" style={bannerLogo} />
            </div>

            <div style={pageStyle}>

                {/* candidate - job detail */}

                <div style={candidateHeaderContainer}>
                {/* Profile pic & candidate Info */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={profilePicStyle}>
                    {(candidateName[0] || '') + (candidateLastName[0] || '')}
                    </div>
                    <div style={candidateInfoContainer}>
                    <h2 style={{ marginBottom: '4px' }}>
                        {(candidateName || 'Candidate')} {(candidateLastName || 'Name')}
                    </h2>
                    <p style={{ margin: 0, fontSize: '16px', color: '#555' }}>{jobTitle || 'Job Title'}</p>
                    <p style={{ margin: 0, fontSize: '14px', color: '#888' }}>Interview ID: {interviewId}</p>
                    </div>
                </div>

                {/* Buttons*/}
                <div style={buttonGroupStyle}>
                    <button style={downloadButtonStyle} onClick={handleDownloadPDF}>
                    Download Report
                    </button>
                    <button style={scheduleButtonStyle}>Schedule Interview</button>
                </div>
                </div>

                

                {report && (
                    <>
                        {/* flexbox for  (progress bar container - recommendation - resume summary) */}
                        <div style={{display: 'flex', gap: '30px', justifyContent: 'center', flexWrap: 'wrap', marginTop: '30px'}}>

                                {/* Candidate Fit Overview */}
                                <div style={{ ...cardStyle, padding: '20px', maxWidth: '500px', flex: 1, borderRadius: '12px',
                                    boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)' }}>
                                  {/* <h2 style={{ marginBottom: '20px', textAlign: 'center' }}> Candidate Fit Overview</h2> */}

                                    {/* Final Score */}
                                    <div style={{ marginBottom: '36px' }}>
                                    <div style={{ fontWeight: 'bold', fontSize: '20px', marginBottom: '10px' }}>
                                        Candidate Fit Score
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                        <div style={{ ...progressBarContainer, height: '15px', flex: 2 }}>
                                        <div style={getProgressBarStyle(finalScore)} />
                                        </div>
                                        <span
                                        style={{
                                            color: getScoreColor(finalScore),
                                            fontWeight: 'bold',
                                            fontSize: '18px',
                                            minWidth: '60px',
                                        }}
                                        >
                                        {finalScore !== null ? `${finalScore}/10` : 'N/A'}
                                        </span>
                                    </div>
                                    </div>

                                    {/* each Category score */}
                                    <div>
                                       {/* <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>Category Scores</div> */}
                                        {scores.filter(item => item.category !== "location")
                                            .map((item, idx) => (
                                                <div key={idx} style={{ marginBottom: '16px' }}>
                                                <div style={{ marginBottom: '4px' }}>{item.category}</div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                    <div style={{ ...progressBarContainer, flex: 1 }}>
                                                    <div style={getProgressBarStyle(item.score)} />
                                                    </div>
                                                    <span style={{ color: getScoreColor(item.score), fontWeight: 'bold', minWidth: '50px' }}>
                                                    {item.score}/10
                                                    </span>
                                                </div>
                                                </div>
                                            ))}
                                    </div>
                                </div>

                                {/* Recommendation */}
                                <div style={{ ...cardStyle, flex: 1, maxWidth: '500px' }}>
                                <h3>Recommendation</h3>
                                <h3 style={{ 
                                    color: report.recommendation === "recommended" ? "#558F8E" : "#dc3545"
                                }}>
                                    {report.recommendation === "recommended" ? "✅ Move to next round" : "❌ Not Recommended"}
                                </h3>
                                <p style={{ fontSize: '18px', lineHeight: '1.5' }}>{report.reason}</p>
                                </div>

                                {/* Resume Summary */}
                                <div style={{ ...cardStyle, flex: 1, maxWidth: '500px' }}>
                                    <h3>Resume Summary</h3>
                                    <p style={{ fontSize: '18px', lineHeight: '1.5' }}>{report.resume_summary}</p> 
                                </div>
                        </div>

                        {/* Centered container for Interview Summary and Key Insights */}
                        <div style={{ marginLeft: '5px', marginTop: '30px' }}>
                            {/* Interview Summary */}
                            <div style={{ ...cardStyle, maxWidth: '1050px', width: '100%' }}>
                                <h3>Interview Summary</h3>
                                <p>{report.interview_summary}</p>
                            </div>

                            {/* Key Insights */}
                            <div style={{ ...cardStyle, maxWidth: '1050px', width: '100%' }}>
                                <h3> Key Insights</h3>
                                <ul>
                                {report.key_insights.map((insight, idx) => (
                                    <li key={idx} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                                    {insight.label === 'good' ? <CheckIcon /> : <CrossIcon />}
                                    <span>{insight.text}</span>
                                    </li>
                                ))}
                                </ul>
                            </div>
                        </div>
                    </>
                )}

                {/*  container for all category details */}
                <div style={{
                marginLeft: '5px',
                padding: '30px',
                backgroundColor: '#fff',
                borderRadius: '16px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                maxWidth: '1025px'
                }}>
                <h2 style={{ marginBottom: '20px' }}>Category Breakdown</h2>

                {scores.map((item, idx) => {
                    const backgroundColor = item.score > 8 ? '#f2fdfb' : '#e4e7eb'; //  green or gray

                    return (
                            <div
                            key={idx}
                            style={{
                                backgroundColor,
                                padding: '20px',
                                borderRadius: '10px',
                                marginBottom: '20px',
                                maxWidth: '1000px',
                            }}
                            >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <h3 style={{ margin: 0 }}>{item.category}</h3>
                                <span style={{ fontWeight: 'bold', fontSize: '18px', color: getScoreColor(item.score) }}>
                                {item.score}/10
                                </span>
                            </div>
                            <p style={{ marginTop: '10px' }}> {item.reason}</p>
                            </div>
                        );
                })}
                </div>



                {/* Transcript button */}
                <button onClick={() => setShowTranscript(!showTranscript)} style={buttonStyle}>
                    {showTranscript ? 'Hide Transcript' : 'View Transcript'}
                </button>

                {/* transcript */}
                {showTranscript && (
                    <div style={transcriptStyle}>
                        <h3>Full Transcript</h3>
                        {transcript.map((t, i) => (
                            <div key={i}>
                                <strong>Q:{t.question} </strong>  <br />
                                <strong>A:</strong> {t.answer} <br /><br />
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CandidateReport;