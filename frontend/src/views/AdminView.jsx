import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Icon } from '../icons/Icons'
import { uploadDocuments, getInventory } from '../api/client'

const DEPARTMENTS = ['general', 'rh', 'operaciones', 'sistemas']
const ACCEPTED_TYPES = '.pdf,.docx,.xlsx,.csv,.md,.html,.htm,.txt'

export default function AdminView({ lang }) {
  const { t } = useTranslation()
  const [inventory, setInventory] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState([])
  const [department, setDepartment] = useState('general')
  const [activeTab, setActiveTab] = useState('upload')
  const [dragOver, setDragOver] = useState(false)

  useEffect(() => {
    loadInventory()
  }, [])

  const loadInventory = async () => {
    try {
      const data = await getInventory()
      setInventory(data)
    } catch {
      setInventory({ items: [], total_documents: 0, total_chunks: 0, total_departments: 0 })
    }
  }

  const handleUpload = async (files) => {
    if (!files || files.length === 0) return
    setUploading(true)
    setResults([])
    try {
      const res = await uploadDocuments(files, department)
      setResults(res.results || [])
      await loadInventory()
    } catch (err) {
      setResults([{ name: 'error', success: false, error: err.message }])
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleUpload(e.dataTransfer.files)
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--main-accent)', marginBottom: '1rem' }}>
        {t('admin_title')}
      </h2>

      <div style={{ display: 'flex', gap: '2px', marginBottom: '1.5rem', background: 'var(--tab-bg)', borderRadius: 'var(--radius-full)', padding: '3px', width: 'fit-content' }}>
        <button className={`header-tab ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}>
          <Icon name="upload" size={14} /> Subir documentos
        </button>
        <button className={`header-tab ${activeTab === 'inventory' ? 'active' : ''}`} onClick={() => setActiveTab('inventory')}>
          <Icon name="database" size={14} /> Inventario
        </button>
      </div>

      {activeTab === 'upload' && (
        <div>
          <div
            className={`upload-zone ${dragOver ? 'dragover' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <Icon name="upload" size={32} className="" />
            <p style={{ marginTop: '0.5rem' }}>{t('admin_upload_label')}</p>
            <p style={{ fontSize: '0.78rem', marginTop: '0.25rem' }}>
              PDF, Word, Excel, CSV, Markdown, HTML, TXT
            </p>
          </div>
          <input
            id="file-input"
            type="file"
            multiple
            accept={ACCEPTED_TYPES}
            style={{ display: 'none' }}
            onChange={(e) => handleUpload(e.target.files)}
          />

          <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--main-muted)' }}>
              {t('admin_department')}:
            </label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              style={{ padding: '0.4rem 0.7rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--chat-border)', background: 'var(--surface)', color: 'var(--main-text)' }}
            >
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>{t(`dept_${d}`)}</option>
              ))}
            </select>
          </div>

          {uploading && <p style={{ marginTop: '1rem', color: 'var(--main-muted)' }}>{t('thinking')}...</p>}

          {results.length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              {results.map((r, i) => (
                <div key={i} style={{ padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)', background: r.success ? 'var(--badge-internal-bg)' : 'var(--badge-error-bg)', color: r.success ? 'var(--badge-internal-text)' : 'var(--badge-error-text)', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                  {r.success ? t('admin_success', { name: r.name, chunks: r.chunks }) : t('admin_error', { name: r.name, error: r.error })}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'inventory' && (
        <div>
          {inventory && inventory.items.length === 0 ? (
            <div className="empty-state">
              <Icon name="database" size={28} />
              <p style={{ marginTop: '0.5rem' }}>{t('admin_empty_inventory')}</p>
            </div>
          ) : inventory && (
            <>
              <div className="admin-stats">
                <div className="stat-card">
                  <div className="stat-num">{inventory.total_documents}</div>
                  <div className="stat-label"><Icon name="database" size={12} /> {t('admin_stat_documents')}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-num">{inventory.total_chunks}</div>
                  <div className="stat-label"><Icon name="database" size={12} /> {t('admin_stat_chunks')}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-num">{inventory.total_departments}</div>
                  <div className="stat-label"><Icon name="briefcase" size={12} /> {t('admin_stat_departments')}</div>
                </div>
              </div>
              <table className="inventory-table">
                <thead>
                  <tr>
                    <th>{t('col_source')}</th>
                    <th>{t('col_department')}</th>
                    <th>{t('col_chunks')}</th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.items.map((item, i) => (
                    <tr key={i}>
                      <td>{item.source}</td>
                      <td>{t(`dept_${item.department}`)}</td>
                      <td>{item.chunks}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}
    </div>
  )
}
