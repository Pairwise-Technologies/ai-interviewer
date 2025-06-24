import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';



const HomeView = () => {
    const [interviews, setInterviews] = useState([]);
    const [selectedInterviewId, setSelectedInterviewId] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        axios.get('/api/interviews/')
            .then(response => {
                setInterviews(response.data);
            })
            .catch(error => {
                console.error('Error fetching interviews:', error);
            });
    }, []);

    const handleSelect = (e) => {
        const id = e.target.value;
        setSelectedInterviewId(id);
        if (id) {
            navigate(`/report/${id}`);
        }
    };

    return (
        <div style={{ backgroundColor: '#202155', minHeight: '100vh', color: 'white', padding: '0', margin: '0' }}>

            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '400px',
                width: '100%',
            }}>
                <img 
                    src="/static/logo3.png"  
                    alt="Logo" 
                    style={{ width: '60%', height: '100%', objectFit: 'contain' }} 
                />
            </div>

            <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'flex-start', 
                paddingTop: '2rem', 
                height: 'calc(100vh - 400px)' 
            }}>
                <p style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
                    Select an Interview to View Report:
                </p>

                {interviews.length === 0 ? (
                    <p>Loading or no interviews found...</p>
                ) : (
                    <select 
                        value={selectedInterviewId} 
                        onChange={handleSelect}
                        style={{
                            padding: '1.2rem',
                            fontSize: '1.2rem',
                            backgroundColor: '#ffffff',
                            color: '#202155',
                            border: 'none',
                            borderRadius: '0px',      
                            minWidth: '350px',        
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
                            cursor: 'pointer'
                        }}
                    >
                        <option value="">-- Select Interview --</option>
                        {interviews.map((interview) => (
                            <option key={interview.id} value={interview.id}>
                                {interview.candidate_name} - {interview.job_title}
                            </option>
                        ))}
                    </select>
                )}
            </div>
        </div>
    );
};

export default HomeView;
