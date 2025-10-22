"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { connectCanvas } from "@/lib/api"

export default function ConnectCanvasPage() {
  const router = useRouter()
  const [canvasBaseUrl, setCanvasBaseUrl] = useState("https://canvas.colorado.edu")
  const [apiToken, setApiToken] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      await connectCanvas(canvasBaseUrl, apiToken)
      // Successful connection, redirect to dashboard
      router.push("/")
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="flex">
        {/* Main Form */}
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="w-full max-w-md">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
                Connect Canvas
              </h1>
              <p className="text-neutral-400 mt-2">
                Link your Canvas account to get started with AI-powered insights.
              </p>
            </div>

            <div className="bg-neutral-900 rounded-lg border border-neutral-800 p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="canvas_base_url" className="block text-sm font-medium text-neutral-300 mb-2">
                    Canvas Base URL
                  </label>
                  <input
                    type="url"
                    id="canvas_base_url"
                    name="canvas_base_url"
                    value={canvasBaseUrl}
                    onChange={(e) => setCanvasBaseUrl(e.target.value)}
                    required
                    className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-md text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="https://university.instructure.com"
                  />
                </div>

                <div>
                  <label htmlFor="canvas_token" className="block text-sm font-medium text-neutral-300 mb-2">
                    Personal Access Token
                  </label>
                  <input
                    type="password"
                    id="canvas_token"
                    name="canvas_token"
                    value={apiToken}
                    onChange={(e) => setApiToken(e.target.value)}
                    required
                    className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-md text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your Canvas access token"
                  />
                </div>

                {error && (
                  <div className="p-3 bg-red-900/20 border border-red-800 rounded-md text-red-300 text-sm">
                    {error}
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Connecting..." : "Connect Canvas"}
                </Button>
              </form>
            </div>
          </div>
        </div>

        {/* Help Panel */}
        <div className="w-96 bg-neutral-900 border-l border-neutral-800 p-6">
          <h2 className="text-lg font-semibold text-white mb-4">How to get your Canvas token</h2>
          
          <div className="space-y-4 text-sm text-neutral-300">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0">
                1
              </div>
              <div>
                <p className="font-medium text-white">Log into Canvas</p>
                <p>Go to your Canvas instance and log in with your credentials.</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0">
                2
              </div>
              <div>
                <p className="font-medium text-white">Go to Account Settings</p>
                <p>Click on &ldquo;Account&rdquo; in the left sidebar, then select &ldquo;Settings&rdquo;.</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0">
                3
              </div>
              <div>
                <p className="font-medium text-white">Create New Access Token</p>
                <p>Scroll down to &ldquo;Approved Integrations&rdquo; and click &ldquo;+ New Access Token&rdquo;.</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0">
                4
              </div>
              <div>
                <p className="font-medium text-white">Generate Token</p>
                <p>Give it a purpose like &ldquo;Canvas AI Labs&rdquo; and click &ldquo;Generate Token&rdquo;.</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0">
                5
              </div>
              <div>
                <p className="font-medium text-white">Copy and Paste</p>
                <p>Copy the generated token and paste it in the form. <strong>Save it somewhere safe!</strong></p>
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-amber-900/20 border border-amber-800 rounded-md">
            <p className="text-xs text-amber-300">
              <strong>Security Note:</strong> Your token will be encrypted and stored securely. 
              Canvas AI Labs never stores tokens in plain text.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
