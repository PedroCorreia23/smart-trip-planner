import './App.css';
import LandingPage from "./LandingPage";
import Home from "./Home";
import { BrowserRouter, Routes, Route } from "react-router-dom";

export default function App() {
  return (
   
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path='/home' element={<Home/>}/>
      </Routes>
      </BrowserRouter>

  );
}

