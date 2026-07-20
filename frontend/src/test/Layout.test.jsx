import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../components/Layout'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        app_caption: 'Mentor técnico 24/7',
        language: 'Idioma',
        theme_dark: '🌙 Tema oscuro',
        theme_light: '☀️ Tema claro',
        tab_chat: 'Chat',
        tab_admin: 'Administración',
        tab_about: 'Acerca de',
        footer_model: 'Modelo activo',
      }
      return translations[key] || key
    },
  }),
}))

function renderLayout(props = {}) {
  return render(
    <BrowserRouter>
      <Layout
        lang="es"
        onLangChange={vi.fn()}
        theme="light"
        onToggleTheme={vi.fn()}
        {...props}
      />
    </BrowserRouter>
  )
}

describe('Layout', () => {
  it('renders language select with both options', () => {
    renderLayout()
    const select = screen.getByRole('combobox')
    expect(select).toBeInTheDocument()
    expect(select).toHaveValue('es')
    expect(screen.getByText('Español')).toBeInTheDocument()
    expect(screen.getByText('Português (BR)')).toBeInTheDocument()
  })

  it('calls onLangChange when selecting Portuguese', async () => {
    const onLangChange = vi.fn()
    renderLayout({ onLangChange })

    const select = screen.getByRole('combobox')
    await userEvent.selectOptions(select, 'pt')

    expect(onLangChange).toHaveBeenCalledWith('pt')
  })

  it('calls onLangChange when selecting Spanish', async () => {
    const onLangChange = vi.fn()
    renderLayout({ onLangChange, lang: 'pt' })

    const select = screen.getByRole('combobox')
    await userEvent.selectOptions(select, 'es')

    expect(onLangChange).toHaveBeenCalledWith('es')
  })
})
