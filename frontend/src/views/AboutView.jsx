import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getAboutInfo } from '../api/client'

export default function AboutView() {
  const { t } = useTranslation()
  // info es null hasta que el backend responda; si el backend no está
  // corriendo, el texto informativo se muestra igual y solo se oculta
  // el resumen técnico (sin bloquear la vista en "Cargando...").
  const [info, setInfo] = useState(null)

  useEffect(() => {
    getAboutInfo().then(setInfo).catch(() => setInfo(null))
  }, [])

  return (
    <div className="about-article">
      <h2 className="about-article-title">{t('about_title')}</h2>

      <p className="about-lead">{t('about_purpose_body')}</p>

      <h3 className="about-section">{t('about_how_title')}</h3>
      <p>{t('about_how_body')}</p>

      <h3 className="about-section">{t('about_tech_title')}</h3>
      <p>{t('about_tech_body')}</p>

      <h3 className="about-section">{t('about_supports_title')}</h3>
      <p>{t('about_supports_body')}</p>

      {info && (
        <>
          <h3 className="about-section">{t('about_tech_summary')}</h3>
          <ul className="about-list">
            <li>
              <strong>{t('about_llm')}:</strong> {info.models?.llm}
              {info.models?.fallbacks?.length > 0 && (
                <span style={{ color: 'var(--main-muted)' }}>
                  {' '}· {t('about_fallbacks')}: {info.models.fallbacks.join(', ')}
                </span>
              )}
            </li>
            <li>
              <strong>{t('about_embeddings')}:</strong> {info.models?.embeddings}
            </li>
            <li>
              <strong>{t('about_k')}:</strong> {info.retrieval?.k} ·{' '}
              <strong>{t('about_threshold')}:</strong> {info.retrieval?.threshold?.toFixed(2)}
            </li>
            <li>
              <strong>{t('about_formats_title')}:</strong>{' '}
              {(info.formats || []).join(', ')}
            </li>
            <li>
              <strong>{t('about_departments_title')}:</strong>{' '}
              {(info.departments || []).map((d) => t(`dept_${d}`)).join(', ')}
            </li>
          </ul>
        </>
      )}
    </div>
  )
}
