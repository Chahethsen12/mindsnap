import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout } from '../services/auth'
import { createSnap, getSnaps, searchSnaps, deleteSnap } from '../services/snaps'

export default function DashboardPage() {
  const [snaps, setSnaps] = useState([])
  const [input, setInput] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadSnaps()
  }, [])

  const loadSnaps = async () => {
    try {
      const res = await getSnaps()
      setSnaps(res.data)
    } catch {
      setError('Failed to load snaps')
    } finally {
      setFetching(false)
    }
  }

  const handleCreate = async () => {
    if (!input.trim()) return
    setLoading(true)
    setError('')
    try {
      await createSnap({ raw_text: input })
      setInput('')
      await loadSnaps()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create snap')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    const q = e.target.value
    setSearch(q)
    if (q.trim()) {
      const res = await searchSnaps(q)
      setSnaps(res.data)
    } else {
      loadSnaps()
    }
  }

  const handleDelete = async (id) => {
    await deleteSnap(id)
    setSnaps(snaps.filter(s => s.id !== id))
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Navbar */}
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-violet-400">⚡ MindSnap</h1>
        <button onClick={handleLogout} className="text-gray-400 hover:text-white text-sm transition">
          Logout
        </button>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {/* Create Snap */}
        <div className="bg-gray-900 rounded-2xl p-6">
          <h2 className="text-lg font-semibold mb-4">Save something new</h2>
          <textarea
            rows={3}
            placeholder="Paste a URL, article text, code snippet, or anything you want to save..."
            value={input}
            onChange={e => setInput(e.target.value)}
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg outline-none focus:ring-2 focus:ring-violet-500 resize-none text-sm"
          />
          {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
          <button
            onClick={handleCreate}
            disabled={loading || !input.trim()}
            className="mt-3 bg-violet-600 hover:bg-violet-700 text-white font-semibold px-6 py-2 rounded-lg transition disabled:opacity-50"
          >
            {loading ? '⚙️ Analyzing...' : '⚡ Snap It'}
          </button>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="🔍 Search your snaps..."
          value={search}
          onChange={handleSearch}
          className="w-full bg-gray-900 text-white px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-violet-500"
        />

        {/* Snaps List */}
        {fetching ? (
          <p className="text-gray-400 text-center">Loading your snaps...</p>
        ) : snaps.length === 0 ? (
          <p className="text-gray-500 text-center">No snaps yet. Save something above!</p>
        ) : (
          <div className="space-y-4">
            {snaps.map(snap => (
              <div key={snap.id} className="bg-gray-900 rounded-2xl p-5 border border-gray-800 hover:border-violet-500/50 transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs bg-violet-500/20 text-violet-300 px-2 py-0.5 rounded-full">
                        {snap.content_type || 'other'}
                      </span>
                    </div>
                    <h3 className="font-semibold text-white">{snap.title}</h3>
                    <p className="text-gray-400 text-sm mt-1">{snap.summary}</p>
                    {snap.tags && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {snap.tags.split(',').map((tag, i) => (
                          <span key={i} className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded-full">
                            {tag.trim()}
                          </span>
                        ))}
                      </div>
                    )}
                    {snap.source_url && (
                      <a href={snap.source_url} target="_blank" rel="noreferrer"
                        className="text-violet-400 text-xs mt-2 block hover:underline">
                        {snap.source_url}
                      </a>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(snap.id)}
                    className="text-gray-600 hover:text-red-400 ml-4 transition text-lg"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}