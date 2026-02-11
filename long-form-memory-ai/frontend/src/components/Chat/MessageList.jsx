import React from 'react'
import { UserCircleIcon, CpuChipIcon, CommandLineIcon } from '@heroicons/react/24/solid'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const MessageList = ({ messages, streamingMessage, isLoading, scrollContainerRef }) => {
  return (
    <div ref={scrollContainerRef} className="flex-1 overflow-y-auto soft-scroll px-3 sm:px-5 py-5">
      {messages.length === 0 && !streamingMessage && (
        <div className="h-full flex items-center justify-center px-4">
          <div className="max-w-2xl w-full surface-panel rounded-3xl p-8 sm:p-12 text-center fade-in-up">
            <div className="h-16 w-16 mx-auto rounded-2xl surface-strong flex items-center justify-center glow-ring">
              <CommandLineIcon className="h-8 w-8 text-[var(--accent)]" />
            </div>
            <h2 className="mt-6 text-3xl sm:text-5xl font-semibold">Welcome to the chat box</h2>
            <p className="mt-4 text-base sm:text-xl text-secondary">
              Start a conversation and I will remember what matters.
            </p>
          </div>
        </div>
      )}

      <div className="max-w-5xl mx-auto space-y-4">
        {messages.map((message, index) => (
          <article
            key={message.id || index}
            className={`surface-panel rounded-2xl p-4 sm:p-5 fade-in-up ${
              message.role === 'user' ? 'message-user' : 'message-assistant'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="shrink-0">
                {message.role === 'user' ? (
                  <UserCircleIcon className="h-8 w-8 text-[var(--accent)]" />
                ) : (
                  <CpuChipIcon className="h-8 w-8 text-secondary" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-sm font-semibold">
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </span>
                  <span className="text-xs text-muted">Turn {message.turn_number}</span>
                </div>
                <div className="prose prose-sm sm:prose-base max-w-none text-[var(--text-primary)] prose-headings:text-[var(--text-primary)] prose-strong:text-[var(--text-primary)] prose-p:text-[var(--text-primary)] prose-li:text-[var(--text-primary)] prose-code:text-[var(--text-primary)]">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          </article>
        ))}

        {streamingMessage && (
          <article className="surface-panel rounded-2xl p-4 sm:p-5 message-assistant fade-in-up">
            <div className="flex items-start gap-3">
              <CpuChipIcon className="h-8 w-8 text-secondary shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="text-sm font-semibold mb-1.5">Assistant</div>
                <div className="whitespace-pre-wrap leading-7 text-[var(--text-primary)]">
                  {streamingMessage}
                  <span className="inline-block h-5 w-2 ml-1 align-middle bg-[var(--accent)] animate-pulse rounded-sm" />
                </div>
              </div>
            </div>
          </article>
        )}

        {isLoading && !streamingMessage && (
          <div className="py-8 flex items-center justify-center">
            <div className="h-8 w-8 rounded-full border-2 border-[var(--border-soft)] border-t-[var(--accent)] animate-spin" />
          </div>
        )}
      </div>
    </div>
  )
}

export default MessageList
