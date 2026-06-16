import { useEffect } from 'react'
import type { Company } from '../types'
import { CompanyCard } from './CompanyCard'

/** Overlay shown when any company name is clicked anywhere in the page. */
export function CompanyModal({ company, onClose }: { company: Company | null; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  if (!company) return null
  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/30 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div className="mt-10 w-full max-w-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="mb-2 flex justify-end">
          <button onClick={onClose} className="rounded-full bg-white px-3 py-1 text-sm shadow hover:bg-gray-50">
            ✕ Close
          </button>
        </div>
        <CompanyCard company={company} />
      </div>
    </div>
  )
}
