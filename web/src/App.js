import React, { Component } from 'react';
import axios from 'axios'
import Button from '@material-ui/core/Button'
import logo from './logo.svg'
import './App.css'

class App extends Component {
  state = {
    selectedFile: null
  }

  handleFileUpload = () => {
    const {selectedFile} = this.state

    const fd = new FormData()
    fd.append('img', selectedFile, selectedFile.name)
    axios.post('localhost:5000/ocr')
    .then(res=>{
      console.log(res)
    })
  }

  handleFileSelect = (event)=>{
    // this.setState({selectedFile: event.target.files[0]})
    console.log("testjasldjflasdjf")
    const selectedFile = event.target.files[0]
    const fd = new FormData()
    fd.append('img', selectedFile, selectedFile.name)
    axios.post('http://localhost:5000/ocr', fd)
      .then(res=>{
          console.log(res)
      })
    console.log("fdfdfdd")
  }

  render() {
    return (
      <div className="App">
        {/* <Button onClick={this.selectImageToUpload}>Upload</Button> */}
        <input type="file" onChange={this.handleFileSelect}/>
      </div>
    );
  }
}

export default App;
