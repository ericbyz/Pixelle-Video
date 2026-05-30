import { spawn } from 'node:child_process'
import { createServer } from 'node:http'
import { Buffer } from 'node:buffer'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createInterface } from 'node:readline'

const __dirname = dirname(fileURLToPath(import.meta.url))
const repoDir = resolve(__dirname, '../..')
const oldDir = resolve(repoDir, 'old')
const python = process.env.PIXELLE_PYTHON || resolve(oldDir, '.venv/bin/python')
const workerPath = resolve(__dirname, 'bridge_worker.py')
const host = process.env.HOST || '127.0.0.1'
const port = Number.parseInt(process.env.BACKEND_PORT || '8000', 10)
const maxBodySize = Number.parseInt(process.env.MAX_UPLOAD_SIZE || `${100 * 1024 * 1024}`, 10)

let nextId = 1
const pending = new Map()

const worker = spawn(python, [workerPath], {
  cwd: repoDir,
  stdio: ['pipe', 'pipe', 'pipe'],
})

worker.stderr.on('data', (chunk) => {
  process.stderr.write(chunk)
})

worker.on('exit', (code, signal) => {
  const error = new Error(`Python bridge worker exited (${signal || code})`)
  for (const { reject } of pending.values()) reject(error)
  pending.clear()
  process.exit(code || 1)
})

createInterface({ input: worker.stdout }).on('line', (line) => {
  let response
  try {
    response = JSON.parse(line)
  } catch (error) {
    console.error('Invalid bridge worker response:', line)
    return
  }

  const entry = pending.get(response.id)
  if (!entry) return
  pending.delete(response.id)
  entry.resolve(response)
})

function readBody(req) {
  return new Promise((resolveBody, rejectBody) => {
    const chunks = []
    let size = 0

    req.on('data', (chunk) => {
      size += chunk.length
      if (size > maxBodySize) {
        rejectBody(new Error('Request body too large'))
        req.destroy()
        return
      }
      chunks.push(chunk)
    })

    req.on('end', () => resolveBody(Buffer.concat(chunks)))
    req.on('error', rejectBody)
  })
}

function sendToWorker(payload) {
  return new Promise((resolveResponse, rejectResponse) => {
    pending.set(payload.id, { resolve: resolveResponse, reject: rejectResponse })
    worker.stdin.write(`${JSON.stringify(payload)}\n`, (error) => {
      if (!error) return
      pending.delete(payload.id)
      rejectResponse(error)
    })
  })
}

const server = createServer(async (req, res) => {
  if (req.headers.upgrade) {
    res.writeHead(426, { 'content-type': 'application/json' })
    res.end(JSON.stringify({ detail: 'WebSocket is not supported by the development bridge' }))
    return
  }

  try {
    const body = await readBody(req)
    const response = await sendToWorker({
      id: nextId++,
      method: req.method,
      url: req.url,
      headers: req.headers,
      body: body.toString('base64'),
    })

    for (const [key, value] of Object.entries(response.headers || {})) {
      res.setHeader(key, value)
    }
    res.statusCode = response.status || 500
    res.end(Buffer.from(response.body || '', 'base64'))
  } catch (error) {
    res.writeHead(500, { 'content-type': 'application/json' })
    res.end(JSON.stringify({ detail: error.message || 'Bridge server error' }))
  }
})

server.listen(port, host, () => {
  console.log(`Pixelle bridge backend listening at http://${host}:${port}`)
})

function shutdown() {
  server.close()
  worker.kill()
}

process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)
