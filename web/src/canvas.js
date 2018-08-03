class Canvas {
  constructor(canvas) {
    this.canvas = canvas
    this.ctx = this.canvas.getContext('2d')
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
  }

  drawImage(img, width, height) {
    this.ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, width, height)
  }

  drawRect(position, scale, fill = false) {
    // xmin, ymin, xmax, ymax
    const p = position.map(x => x / scale)

    const x = p[0]
    const y = p[1]
    const w = p[2] - p[0]
    const h = p[3] - p[1]

    if (fill) {
      this.ctx.fillRect(x, y, w, h)
    } else {
      this.ctx.strokeRect(x, y, w, h)
    }
  }

  setWidth(width) {
    this.canvas.width = width
  }

  setHeight(height) {
    this.canvas.height = height
  }

  setLineWidth(lineWidth) {
    this.ctx.lineWidth = lineWidth
  }

  setStrokeColor(r, g, b) {
    this.ctx.strokeStyle = `rgb(${r},${g},${b})`
  }

  setFillColor(r, g, b, a) {
    this.ctx.fillStyle = `rgba(${r},${g},${b},0.3)`
  }
}

export default Canvas
