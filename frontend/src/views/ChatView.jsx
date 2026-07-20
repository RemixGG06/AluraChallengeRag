import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import ReactMarkdown from 'react-markdown'
import { Icon } from '../icons/Icons'
import { sendMessage } from '../api/client'

const BADGE_MAP = {
  internal: { icon: 'file', class: 'badge-internal', labelKey: 'badge_internal' },
  web: { icon: 'globe', class: 'badge-web', labelKey: 'badge_web' },
  inventory: { icon: 'book', class: 'badge-internal', labelKey: 'badge_inventory' },
  none: { icon: 'message', class: 'badge-assistant', labelKey: 'badge_assistant' },
  error: { icon: 'alert', class: 'badge-error', labelKey: 'badge_error' },
}

export default function ChatView({ lang }) {
  const { t } = useTranslation()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showSources, setShowSources] = useState(true)
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const question = input.trim()
    if (!question || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const history = messages.slice(-10).map((m) => ({ role: m.role, content: m.content }))
      const res = await sendMessage(question, history, lang)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          source_type: res.source_type,
          sources: res.sources || [],
          model: res.model,
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: t('badge_error'), source_type: 'error', sources: [] },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => setMessages([])

  const latestSources = (() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'assistant' && messages[i].sources?.length > 0) {
        return { sources: messages[i].sources, type: messages[i].source_type }
      }
    }
    return { sources: [], type: 'none' }
  })()

  return (
    <div className="chat-view">
      <div className="chat-header">
        <h2>{t('chat_title')}</h2>
        {messages.length > 0 && (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn" onClick={() => setShowSources(!showSources)}>
              <Icon name="book" size={14} /> {showSources ? 'Ocultar fuentes' : 'Ver fuentes'}
            </button>
            <button className="btn" onClick={handleClear}>
              <Icon name="trash" size={14} /> {t('clear_chat')}
            </button>
          </div>
        )}
      </div>

      {messages.length === 0 && <div className="welcome-box">{t('chat_welcome')}</div>}

      <div className={`chat-container ${showSources ? 'with-sources' : ''}`}>
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className="message">
              <div className={`message-avatar ${msg.role}`}>
                {msg.role === 'user' ? 'U' : 'AI'}
              </div>
              <div>
                <div className="message-bubble"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
                {msg.role === 'assistant' && (
                  <span className={`badge ${BADGE_MAP[msg.source_type]?.class || 'badge-assistant'}`}>
                    <Icon name={BADGE_MAP[msg.source_type]?.icon || 'message'} size={12} />
                    {t(BADGE_MAP[msg.source_type]?.labelKey || 'badge_assistant')}
                  </span>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message">
              <div className="message-avatar assistant">AI</div>
              <div className="message-bubble" style={{ color: 'var(--main-muted)' }}>
                {t('thinking')}...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {showSources && (
          <div className="sources-panel">
            <div className="sources-title">
              <Icon name="book" size={20} /> {t('sources_panel_title')}
            </div>
            {latestSources.sources.length === 0 ? (
              <p style={{ color: 'var(--main-muted)', fontSize: '0.85rem' }}>{t('no_sources_yet')}</p>
            ) : (
              latestSources.sources.map((src, idx) => (
                <div key={idx} className="source-card">
                  <div className="source-name">
                    <Icon name={latestSources.type === 'web' ? 'globe' : 'file'} size={14} />
                    {' '}
                    {latestSources.type === 'web' ? (
                      <a href={src.url} target="_blank" rel="noopener noreferrer">{src.source}</a>
                    ) : (
                      src.source
                    )}
                  </div>
                  {latestSources.type === 'internal' && (
                    <>
                      <div className="source-detail">
                        <Icon name="briefcase" size={12} /> {t(`dept_${src.department || 'general'}`)}
                      </div>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${(src.score || 0) * 100}%` }} />
                      </div>
                      <div className="source-detail" style={{ marginTop: '0.25rem' }}>
                        {t('confidence_label')}: {((src.score || 0) * 100).toFixed(0)}%
                      </div>
                    </>
                  )}
                  {latestSources.type === 'web' && (
                    <div className={src.trusted ? 'trusted' : 'untrusted'}>
                      <Icon name={src.trusted ? 'shield' : 'alert'} size={12} />
                      {' '}
                      {src.trusted ? t('trusted_label') : t('untrusted_label')}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <div className="message-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={t('chat_input_placeholder')}
          disabled={loading}
        />
      </div>
    </div>
  )
}
