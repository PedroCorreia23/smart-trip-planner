import './App.css';
import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
  const nav = useNavigate()
  const navigate=()=>{
    nav("/home")
  }
  return (
    <div className="landing-page">
      <h1>SMART TRIP PLANNER</h1>
      <h2>Are you ready for your next trip?</h2>
      <button onClick={navigate}>Let's Go!</button>
    </div>
  );
}

