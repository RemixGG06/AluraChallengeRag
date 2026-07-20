import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockChangeLanguage, getCurrentLang, setCurrentLang, translations } = vi.hoisted(() => {
  let currentLang = 'es'
  const translations = {
    es: {
      app_caption: 'Mentor técnico 24/7 para el onboarding de practicantes de TI',
      language: 'Idioma',
      tab_chat: 'Chat',
      tab_admin: 'Administración',
      chat_title: 'Asistente de onboarding',
      chat_welcome: '¡Hola! Soy tu mentor técnico.',
      theme_dark: '🌙 Tema oscuro',
      theme_light: '☀️ Tema claro',
      footer_model: 'Modelo activo',
    },
    pt: {
      app_caption: 'Mentor técnico 24/7 para o onboarding de estagiários de TI',
      language: 'Idioma',
      tab_chat: 'Chat',
      tab_admin: 'Administração',
      chat_title: 'Assistente de onboarding',
      chat_welcome: 'Olá! Sou seu mentor técnico.',
      theme_dark: '🌙 Tema escuro',
      theme_light: '☀️ Tema claro',
      footer_model: 'Modelo ativo',
    },
  }
  return {
    mockChangeLanguage: vi.fn((lang) => {
      currentLang = lang
    }),
    getCurrentLang: () => currentLang,
    setCurrentLang: (lang) => { currentLang = lang },
    translations,
  }
})

vi.mock('react-i18next', () => ({
  initReactI18next: { type: '3rdParty', init: vi.fn() },
  useTranslation: () => ({
    t: (key) => translations[getCurrentLang()]?.[key] || key,
    i18n: {
      changeLanguage: mockChangeLanguage,
      language: getCurrentLang(),
    },
  }),
}))

vi.mock('../i18n', () => ({
  default: {
    changeLanguage: mockChangeLanguage,
    language: getCurrentLang(),
  },
}))

import App from '../App'

describe('App language switching', () => {
  beforeEach(() => {
    localStorage.clear()
    setCurrentLang('es')
    mockChangeLanguage.mockClear()
  })

  it('renders with Spanish text by default', () => {
    render(<App />)
    expect(screen.getByText('Chat')).toBeInTheDocument()
    expect(screen.getByText('Administración')).toBeInTheDocument()
    expect(screen.getByText('Asistente de onboarding')).toBeInTheDocument()
  })

  it('switches to Portuguese and updates sidebar', async () => {
    render(<App />)
    const select = screen.getByRole('combobox')
    await userEvent.selectOptions(select, 'pt')

    await waitFor(() => {
      expect(screen.getByText(/Administração/)).toBeInTheDocument()
    })
  })

  it('persists language to localStorage on change', async () => {
    render(<App />)
    const select = screen.getByRole('combobox')
    await userEvent.selectOptions(select, 'pt')

    expect(localStorage.getItem('lang')).toBe('pt')
  })

  it('reads initial language from localStorage', () => {
    localStorage.setItem('lang', 'pt')
    render(<App />)
    const select = screen.getByRole('combobox')
    expect(select).toHaveValue('pt')
  })
})
