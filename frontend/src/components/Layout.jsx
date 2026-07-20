import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Icon } from '../icons/Icons'

const TABS = [
  { path: '/chat', key: 'tab_chat' },
  { path: '/admin', key: 'tab_admin' },
  { path: '/about', key: 'tab_about' },
]

export default function Layout({ children, lang, onLangChange, theme, onToggleTheme }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <img src="/LogoSinfondoChallenge.svg" alt="Logo" style={{ width: 120 }} />
        <div className="sidebar-brand">
          MentorTI <span>Nexus</span>
        </div>
        <span className="sidebar-caption">{t('app_caption')}</span>
        <hr className="sidebar-divider" />
        <label style={{ fontSize: '0.8rem', color: 'var(--sidebar-muted)' }}>{t('language')}</label>
        <select value={lang} onChange={(e) => onLangChange(e.target.value)}>
          <option value="es">Español</option>
          <option value="pt">Português (BR)</option>
        </select>
        <hr className="sidebar-divider" />
        <button onClick={onToggleTheme}>
          {theme === 'light' ? t('theme_dark') : t('theme_light')}
        </button>
      </aside>

      <header className="header">
        <div className="header-brand">
          <h1>MentorTI <span>Nexus</span></h1>
          <small>{t('app_caption')}</small>
        </div>
        <nav className="header-tabs">
          {TABS.map((tab) => (
            <button
              key={tab.path}
              className={`header-tab ${location.pathname === tab.path ? 'active' : ''}`}
              onClick={() => navigate(tab.path)}
            >
              {t(tab.key)}
            </button>
          ))}
        </nav>
        <div className="header-actions">
          <button className="icon-btn" onClick={onToggleTheme} title={t('theme_light')}>
            <Icon name={theme === 'light' ? 'moon' : 'sun'} size={18} />
          </button>
        </div>
      </header>

      <main className="content">
        {children}
      </main>

      <footer className="footer">
        <span><Icon name="cpu" size={12} /> {t('footer_model')}: gemma-4-26b-a4b-it:free</span>
        <span><Icon name="chat" size={12} /> MentorTI Nexus v1.0</span>
      </footer>
    </div>
  )
}
