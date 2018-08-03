import React, { Component } from 'react'
import axios from 'axios'
import Button from '@material-ui/core/Button'
import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import Grid from '@material-ui/core/Grid'
import { withStyles } from '@material-ui/core/styles'
import Paper from '@material-ui/core/Paper'

import Canvas from './canvas'

const styles = theme => ({
  root: {
    flexGrow: 1,
    paddingTop: 150,
    paddingLeft: 150,
    paddingRight: 150,
    height: '100%',
    backgroundColor: '#fafafa'
  },
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
    minHeight: 600,
    maxHeight: 600,
    overflowY: 'auto'
  },
  img: {
    visibility: 'hidden',
    display: 'none'
  },
  tableWrapper: {
    overflowY: 'auto'
  },
  table: {
    minWidth: 300
  },
  tableHead: {
    // backgroundColor: theme.palette.common.black,
    // color: theme.palette.common.white
  },
  input: {
    display: 'none'
  },
  inputBtn: {
    display: 'flex',
    justifyContent: 'center'
  }
})

class App extends Component {
  MAX_WIDTH = 700
  MAX_HEIGHT = 600

  state = {
    image: null,
    ocrResult: []
  }

  componentDidMount() {
    const img = this.refs.image
    this.canvas = new Canvas(this.refs.canvas)

    img.onload = () => {
      this.findBestImgSize(img)
      this.canvas.drawImage(img, this.sWidth, this.sHeight)
    }
  }

  handleFileSelect = event => {
    const selectedFile = event.target.files[0]

    let reader = new FileReader()
    reader.onload = e => {
      this.setState({ image: e.target.result })
    }
    reader.readAsDataURL(selectedFile)

    const fd = new FormData()
    fd.append('img', selectedFile, selectedFile.name)
    axios.post('http://localhost:5000/ocr', fd).then(res => {
      this.setState({ ocrResult: res.data.results })
      this.drawPositions(res.data.results)
    })
  }

  drawPositions(results) {
    results.forEach(r => {
      this.canvas.drawRect(r.position, this.scale)
    })
  }

  findBestImgSize(img) {
    let wScale = 1
    let hScale = 1
    if (img.width > this.MAX_WIDTH) {
      wScale = img.width / this.MAX_WIDTH
    }
    if (img.height > this.MAX_HEIGHT) {
      hScale = img.height / this.MAX_HEIGHT
    }

    this.scale = Math.max(wScale, hScale)
    this.sWidth = img.width / this.scale
    this.sHeight = img.height / this.scale

    this.canvas.setWidth(this.sWidth)
    this.canvas.setHeight(this.sHeight)
    this.canvas.setStrokeColor(0, 255, 0)
  }

  getPositionStr(position) {
    return `${position[0]}, ${position[1]}, ${position[2]}, ${position[3]}`
  }

  render() {
    const { classes } = this.props
    const { image, ocrResult } = this.state

    return (
      <div className={classes.root}>
        <Grid container spacing={24}>
          <Grid item xs={12} className={classes.inputBtn}>
            <input
              type="file"
              onChange={this.handleFileSelect}
              id="contained-button-file"
              className={classes.input}
            />
            <label htmlFor="contained-button-file">
              <Button variant="contained" component="span" color="primary">
                Choose Image
              </Button>
            </label>
          </Grid>
          <Grid item xs={6}>
            <Paper className={classes.paper}>
              <canvas ref="canvas" />
              <img src={image} ref="image" className={classes.img} />
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper className={classes.paper}>
              <div className={classes.tableWrapper}>
                <Table className={classes.table}>
                  <TableHead className={classes.tableHead}>
                    <TableRow>
                      <TableCell>Text</TableCell>
                      <TableCell>Position</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ocrResult.map((n, i) => {
                      return (
                        <TableRow key={i}>
                          <TableCell>{n.text}</TableCell>
                          <TableCell>
                            {this.getPositionStr(n.position)}
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </div>
            </Paper>
          </Grid>
        </Grid>
      </div>
    )
  }
}

export default withStyles(styles)(App)
