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
import logo from './logo.svg'
import './App.css'

const styles = theme => ({
  root: {
    flexGrow: 1,
    paddingTop: 150,
    paddingLeft: 150,
    paddingRight: 150
  },
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
    minHeight: 500
  },
  img: {
    maxWidth: 600
  },
  table: {
    minWidth: 300
  }
})

class App extends Component {
  state = {
    image: null,
    ocrResult: []
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
    })
  }

  render() {
    const { classes } = this.props
    const { image, ocrResult } = this.state
    console.log(ocrResult)

    return (
      <div className={classes.root}>
        <input type="file" onChange={this.handleFileSelect} />
        <Grid container spacing={24}>
          <Grid item xs={6}>
            <Paper className={classes.paper}>
              <img src={image} className={classes.img} />
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper className={classes.paper}>
              <Table className={classes.table}>
                <TableHead>
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
                        <TableCell>{n.position}</TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </Paper>
          </Grid>
        </Grid>
      </div>
    )
  }
}

export default withStyles(styles)(App)
