import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import App from './App.tsx'
import LandingPage from './components/ui/hero.tsx'
import DocsPage from './components/ui/docs.tsx'
import './index.css'
import { ThemeProvider } from "./components/theme-provider"

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<App />} />
          <Route path="/docs" element={<DocsPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  </React.StrictMode>,
)
