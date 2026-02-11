import React from 'react'
import { LightBulbIcon } from '@heroicons/react/24/outline'

const MemoryIndicator = ({ count, memories }) => {
  if (!count || count === 0) return null

  return (
    <div className="surface-panel rounded-xl p-3 mb-4">
      <div className="flex items-center space-x-2 mb-2">
        <LightBulbIcon className="h-5 w-5 text-[var(--accent)]" />
        <span className="text-sm font-medium">
          Active Memories ({count})
        </span>
      </div>
      <div className="space-y-1">
        {memories?.map((mem, idx) => (
          <div key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium surface-strong text-secondary mr-2">
            {mem.type}: {mem.content}
          </div>
        ))}
      </div>
    </div>
  )
}

export default MemoryIndicator
