import { describe, it, expect } from 'vitest'
import es from '../i18n/es.json'
import pt from '../i18n/pt.json'

describe('i18n consistency', () => {
  it('es.json and pt.json should have the same keys', () => {
    const esKeys = Object.keys(es).sort()
    const ptKeys = Object.keys(pt).sort()

    const missingInPt = esKeys.filter((k) => !(k in pt))
    const missingInEs = ptKeys.filter((k) => !(k in es))

    expect(missingInPt, `Keys missing in pt.json: ${missingInPt.join(', ')}`).toEqual([])
    expect(missingInEs, `Keys missing in es.json: ${missingInEs.join(', ')}`).toEqual([])
  })

  it('should have at least one translation for common UI keys', () => {
    const requiredKeys = ['app_caption', 'tab_chat', 'language', 'chat_title']
    requiredKeys.forEach((key) => {
      expect(es[key]).toBeDefined()
      expect(pt[key]).toBeDefined()
    })
  })
})
