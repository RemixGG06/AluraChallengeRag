const API_BASE = import.meta.env.VITE_API_URL || '/api'

export async function sendMessage(question, history = [], lang = 'es') {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history, lang }),
  })
  if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)
  return res.json()
}

export async function uploadDocuments(files, department = 'general') {
  const formData = new FormData()
  for (const file of files) formData.append('files', file)
  formData.append('department', department)

  const res = await fetch(`${API_BASE}/admin/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)
  return res.json()
}

export async function getInventory() {
  const res = await fetch(`${API_BASE}/admin/inventory`)
  if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)
  return res.json()
}

export async function getAboutInfo() {
  const res = await fetch(`${API_BASE}/about`)
  if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)
  return res.json()
}
