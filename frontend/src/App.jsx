import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import i18n from './i18n'
import Layout from './components/Layout'
import ChatView from './views/ChatView'
import AdminView from './views/AdminView'
import AboutView from './views/AboutView'

export default function App() {
  const [lang, setLang] = useState(() => localStorage.getItem('lang') || 'es')
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')

  const toggleTheme = () => {
    const next = theme === 'light' ? 'dark' : 'light'
    setTheme(next)
    localStorage.setItem('theme', next)
    document.documentElement.setAttribute('data-theme', next)
  }

  const changeLang = (newLang) => {
    setLang(newLang)
    localStorage.setItem('lang', newLang)
    i18n.changeLanguage(newLang)
  }

  return (
    <BrowserRouter>
      <Layout lang={lang} onLangChange={changeLang} theme={theme} onToggleTheme={toggleTheme}>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatView lang={lang} />} />
          <Route path="/admin" element={<AdminView lang={lang} />} />
          <Route path="/about" element={<AboutView lang={lang} />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
