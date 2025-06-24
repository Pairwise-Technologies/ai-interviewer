import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import HomeView from '../views/HomeView';
import CandidateReport from './CandidateReport';

import { useParams } from 'react-router-dom';

const CandidateReportWrapper = () => {
    const { interviewId } = useParams();
    return <CandidateReport interviewId={interviewId} />;
};

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomeView />} />
                <Route path="/report/:interviewId" element={<CandidateReportWrapper />} />
            </Routes>
        </Router>
    );
}

export default App;

